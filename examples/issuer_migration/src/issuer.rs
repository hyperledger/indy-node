use crate::{
    ledger::{BesuLedger, IndyLedger, Ledgers},
    wallet::{BesuWallet, IndyWallet},
};
use indy2_vdr::{
    did::{VerificationKey, VerificationKeyType},
    DidDocument, Service, ServiceEndpoint, StringOrVector, VerificationMethod,
    VerificationMethodOrReference,
};
use serde_json::json;
use std::time::Duration;
use indy2_vdr::did::DID;
use vdrtoolsrs::future::Future;

pub struct Issuer {
    pub indy_wallet: IndyWallet,
    pub indy_ledger: IndyLedger,
    pub besu_ledger: BesuLedger,
    pub did: String,
    pub account: String,
    pub edkey: String,
    pub secpkey: String,
    pub service: String,
    pub used_ledger: Ledgers,
}

impl Issuer {
    const NAME: &'static str = "issuer";

    const SCHEMA_NAME: &'static str = "test_credential";
    const SCHEMA_VERSION: &'static str = "1.0.0";
    const SCHEMA_ATTRIBUTES: &'static str = r#"["first_name", "last_name"]"#;
    const CREDENTIAL_VALUES: &'static str = r#"{"first_name": {"raw": "alice", "encoded":"3987245649832503"}, "last_name": {"raw": "clarck", "encoded": "45436456457657"}}"#;

    pub const SECP_PRIVATE_KEY: &'static str =
        "8bbbb1b345af56b560a5b20bd4b0ed1cd8cc9958a16262bc75118453cb546df7";
    pub const SERVICE_ENDPOINT: &'static str = "127.0.0.1:5555";

    pub async fn setup() -> Issuer {
        let indy_wallet = IndyWallet::new(Self::NAME);
        let indy_ledger = IndyLedger::new(Self::NAME);
        let besu_wallet = BesuWallet::new(Some(Self::SECP_PRIVATE_KEY));
        let account = besu_wallet.account.clone();
        let secpkey = besu_wallet.secpkey.clone();
        let besu_ledger = BesuLedger::new(besu_wallet).await;
        let (did, verkey) = vdrtoolsrs::did::create_and_store_my_did(indy_wallet.handle, "{}")
            .wait()
            .unwrap();
        Issuer {
            indy_wallet,
            besu_ledger,
            indy_ledger,
            did,
            edkey: verkey,
            account,
            secpkey,
            used_ledger: Ledgers::Indy,
            service: Self::SERVICE_ENDPOINT.to_string(),
        }
    }

    pub fn publish_attrib(&self, attrib: &str) {
        let request = vdrtoolsrs::ledger::build_attrib_request(
            &self.did,
            &self.did,
            None,
            Some(attrib),
            None,
        )
        .wait()
        .unwrap();
        let _response = vdrtoolsrs::ledger::sign_and_submit_request(
            self.indy_ledger.handle,
            self.indy_wallet.handle,
            &self.did,
            &request,
        )
        .wait()
        .unwrap();
        std::thread::sleep(Duration::from_millis(500));
    }

    pub fn publish_service_endpoint(&self, endpoint: &str) {
        let endpoint = json!({
            "endpoint":{
                "ha": endpoint
            }
        })
        .to_string();
        self.publish_attrib(&endpoint)
    }

    pub fn publish_besu_ledger_account(&self, key: &str) {
        let key = json!({
            "besu":{
                "key": key
            }
        })
        .to_string();
        self.publish_attrib(&key)
    }

    pub fn create_schema(&self) -> (String, String) {
        let (schema_id, schema) = vdrtoolsrs::anoncreds::issuer_create_schema(
            &self.did,
            Self::SCHEMA_NAME,
            Self::SCHEMA_VERSION,
            Self::SCHEMA_ATTRIBUTES,
        )
        .wait()
        .unwrap();
        let request = vdrtoolsrs::ledger::build_schema_request(&self.did, &schema)
            .wait()
            .unwrap();
        let _response = vdrtoolsrs::ledger::sign_and_submit_request(
            self.indy_ledger.handle,
            self.indy_wallet.handle,
            &self.did,
            &request,
        )
        .wait()
        .unwrap();
        std::thread::sleep(Duration::from_millis(500));
        (schema_id, schema)
    }

    pub fn create_cred_def(&self, schema_id: &str) -> (String, String) {
        let (_, schema) = self.indy_ledger.get_schema(schema_id);
        let (cred_def_id, cred_def) =
            vdrtoolsrs::anoncreds::issuer_create_and_store_credential_def(
                self.indy_wallet.handle,
                &self.did,
                &schema,
                "default",
                None,
                "{}",
            )
            .wait()
            .unwrap();
        let request = vdrtoolsrs::ledger::build_cred_def_request(&self.did, &cred_def)
            .wait()
            .unwrap();
        let _response = vdrtoolsrs::ledger::sign_and_submit_request(
            self.indy_ledger.handle,
            self.indy_wallet.handle,
            &self.did,
            &request,
        )
        .wait()
        .unwrap();
        std::thread::sleep(Duration::from_millis(500));
        (cred_def_id, cred_def)
    }

    pub fn create_credential_offer(&self, cred_def_id: &str) -> String {
        vdrtoolsrs::anoncreds::issuer_create_credential_offer(self.indy_wallet.handle, cred_def_id)
            .wait()
            .unwrap()
    }

    pub fn sign_credential(&self, cred_offer: &str, cred_request: &str) -> String {
        let (credential, _, _) = vdrtoolsrs::anoncreds::issuer_create_credential(
            self.indy_wallet.handle,
            cred_offer,
            cred_request,
            Issuer::CREDENTIAL_VALUES,
            None,
            -1,
        )
        .wait()
        .unwrap();
        credential
    }

    pub fn build_did_doc(did: &str, edkey: &str, secpkey: &str, endpoint: &str) -> DidDocument {
        let id = DID::build("testnet", did);
        let kid_ed = format!("{}#KEY-1", id.value());
        let kid_secp = format!("{}#KEY-2", id.value());
        DidDocument {
            context: StringOrVector::Vector(vec!["https://www.w3.org/ns/did/v1".to_string()]),
            id: id.clone(),
            controller: StringOrVector::Vector(vec![]),
            verification_method: vec![
                VerificationMethod {
                    id: kid_ed.clone(),
                    type_: VerificationKeyType::Ed25519VerificationKey2018,
                    controller: id.value().to_string(),
                    verification_key: VerificationKey::Multibase {
                        public_key_multibase: edkey.to_string(),
                    },
                },
                VerificationMethod {
                    id: kid_secp.clone(),
                    type_: VerificationKeyType::EcdsaSecp256k1VerificationKey2019,
                    controller: id.value().to_string(),
                    verification_key: VerificationKey::Multibase {
                        public_key_multibase: secpkey.to_string(),
                    },
                },
            ],
            authentication: vec![
                VerificationMethodOrReference::String(kid_ed.clone()),
                VerificationMethodOrReference::String(kid_secp.clone()),
            ],
            assertion_method: vec![],
            capability_invocation: vec![],
            capability_delegation: vec![],
            key_agreement: vec![],
            service: vec![Service {
                id: "#inline".to_string(),
                type_: "DIDCommService".to_string(),
                service_endpoint: ServiceEndpoint::String(endpoint.to_string()),
            }],
            also_known_as: Some(vec![]),
        }
    }

    pub fn use_indy_ledger(&mut self) {
        self.used_ledger = Ledgers::Indy
    }

    pub fn use_besu_ledger(&mut self) {
        self.used_ledger = Ledgers::Besu
    }
}
