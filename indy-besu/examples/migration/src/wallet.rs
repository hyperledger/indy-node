use indy2_vdr::{Address, BasicSigner};
use serde_json::json;
use vdrtoolsrs::{future::Future, WalletHandle};

pub struct IndyWallet {
    pub handle: WalletHandle,
}

impl IndyWallet {
    pub const KEY: &'static str = "8dvfYSt5d1taSd6yJdpjq4emkwsPDDLYxkNFysFD2cZY";
    pub const KEY_DERIVATION: &'static str = "RAW";

    pub fn new(name: &str) -> IndyWallet {
        let config = json!({ "id": format!("{}_wallet", name) }).to_string();
        let credentials = json!({
            "key": Self::KEY,
            "key_derivation_method": Self::KEY_DERIVATION
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
    pub account: Address,
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
