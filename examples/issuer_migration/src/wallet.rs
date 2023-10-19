use indy2_vdr::BasicSigner;
use serde_json::json;
use vdrtoolsrs::{future::Future, WalletHandle};

pub struct IndyWallet {
    pub handle: WalletHandle,
}

impl IndyWallet {
    pub fn new(name: &str) -> IndyWallet {
        let config = json!({
            "id": format!("{}_wallet", name)
        })
        .to_string();
        let credentials = json!({
            "key": "8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY",
            "key_derivation_method":"RAW"
        })
        .to_string();
        vdrtoolsrs::wallet::create_wallet(&config, &credentials)
            .wait()
            .ok();
        let handle = vdrtoolsrs::wallet::open_wallet(&config, &credentials)
            .wait()
            .unwrap();
        IndyWallet { handle }
    }
}

pub struct BesuWallet {
    pub account: String,
    pub secpkey: String,
    pub signer: BasicSigner,
}

impl BesuWallet {
    pub fn new(private_key: Option<&str>) -> BesuWallet {
        let mut signer = BasicSigner::new().unwrap();
        let (account, public_key) = signer.create_key(private_key).unwrap();
        let secpkey = bs58::encode(public_key).into_string();
        BesuWallet {
            account,
            secpkey,
            signer,
        }
    }
}
