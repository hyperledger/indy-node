use crate::{
    ledger::{IndyLedger, Ledgers},
    wallet::IndyWallet,
};
use serde_json::json;
use std::time::Duration;
use vdrtoolsrs::future::Future;

pub struct Trustee {
    indy_wallet: IndyWallet,
    indy_ledger: IndyLedger,
    did: String,
    used_ledger: Ledgers,
}

impl Trustee {
    const NAME: &'static str = "trustee";

    pub fn setup(seed: &str) -> Trustee {
        let indy_wallet = IndyWallet::new(Self::NAME);
        let indy_ledger = IndyLedger::new(Self::NAME);
        let config = json!({ "seed": seed }).to_string();
        let (did, _) = vdrtoolsrs::did::create_and_store_my_did(indy_wallet.handle, &config)
            .wait()
            .unwrap();
        Trustee {
            indy_wallet,
            indy_ledger,
            did,
            used_ledger: Ledgers::Indy,
        }
    }

    pub fn publish_did(&self, did: &str, verkey: &str) {
        let request = vdrtoolsrs::ledger::build_nym_request(
            &self.did,
            &did,
            Some(&verkey),
            None,
            Some("ENDORSER"),
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

    pub fn use_indy_ledger(&mut self) {
        self.used_ledger = Ledgers::Indy
    }

    pub fn use_besu_ledger(&mut self) {
        self.used_ledger = Ledgers::Besu
    }
}
