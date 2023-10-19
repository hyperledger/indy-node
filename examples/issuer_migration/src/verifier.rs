use crate::{
    ledger::{BesuLedger, IndyLedger, Ledgers},
    wallet::{BesuWallet, IndyWallet},
};
use indy2_vdr::{
    migration::{IndyCredentialDefinitionFormat, IndySchemaFormat},
    CredentialDefinitionId, SchemaId,
};
use serde_json::json;
use vdrtoolsrs::future::Future;

pub struct Verifier {
    pub indy_wallet: IndyWallet,
    pub indy_ledger: IndyLedger,
    pub besu_ledger: BesuLedger,
    pub did: String,
    pub verkey: String,
    pub used_ledger: Ledgers,
}

impl Verifier {
    const NAME: &'static str = "verifier";

    pub async fn setup() -> Verifier {
        let indy_wallet = IndyWallet::new(Self::NAME);
        let indy_ledger = IndyLedger::new(Self::NAME);
        let besu_wallet = BesuWallet::new(None);
        let besu_ledger = BesuLedger::new(besu_wallet).await;
        let (did, verkey) = vdrtoolsrs::did::create_and_store_my_did(indy_wallet.handle, "{}")
            .wait()
            .unwrap();
        Verifier {
            indy_wallet,
            indy_ledger,
            besu_ledger,
            did,
            verkey,
            used_ledger: Ledgers::Indy,
        }
    }

    pub fn request() -> String {
        json!({
           "nonce":"123432421212",
           "name":"proof_req_1",
           "version":"0.1",
           "requested_attributes": {
                "attr1_referent": {
                    "name": "first_name"
                }
           },
           "requested_predicates": {}
        })
        .to_string()
    }

    pub async fn verify_proof(&self, proof_request: &str, proof: &str) -> bool {
        let parsed_proof = serde_json::from_str::<serde_json::Value>(proof).unwrap();
        let identifier = parsed_proof["identifiers"][0].as_object().unwrap();
        let schema_id = identifier["schema_id"].as_str().unwrap();
        let cred_def_id = identifier["cred_def_id"].as_str().unwrap();

        let (schema, cred_def) = match self.used_ledger {
            Ledgers::Indy => {
                let (_, schema) = self.indy_ledger.get_schema(&schema_id);
                let (_, cred_def) = self.indy_ledger.get_cred_def(&cred_def_id);
                (schema, cred_def)
            }
            Ledgers::Besu => {
                let schema_id = SchemaId::from_indy_format(schema_id);
                let cred_def_id = CredentialDefinitionId::from_indy_format(cred_def_id);
                let schema = self.besu_ledger.get_schema(&schema_id).await;
                let cred_def = self.besu_ledger.get_cred_def(&cred_def_id).await;
                let schema: IndySchemaFormat = schema.into();
                let cred_def: IndyCredentialDefinitionFormat = cred_def.into();
                (json!(schema).to_string(), json!(cred_def).to_string())
            }
        };

        let schemas_json =
            json!({schema_id: serde_json::from_str::<serde_json::Value>(&schema).unwrap()})
                .to_string();
        let cred_defs_json =
            json!({cred_def_id: serde_json::from_str::<serde_json::Value>(&cred_def).unwrap()})
                .to_string();

        vdrtoolsrs::anoncreds::verifier_verify_proof(
            &proof_request,
            proof,
            &schemas_json,
            &cred_defs_json,
            "{}",
            "{}",
        )
        .wait()
        .unwrap()
    }

    pub fn use_indy_ledger(&mut self) {
        self.used_ledger = Ledgers::Indy
    }

    pub fn use_besu_ledger(&mut self) {
        self.used_ledger = Ledgers::Besu
    }
}
