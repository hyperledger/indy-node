use crate::{
    error::{VdrError, VdrResult},
    signer::Signer,
};

use secp256k1::{ecdsa::RecoveryId, All, Message, PublicKey, Secp256k1, SecretKey};
use std::collections::HashMap;

#[cfg(test)]
use std::str::FromStr;
#[cfg(test)]
use web3::signing::keccak256;

pub struct KeyPair {
    public_key: PublicKey,
    private_key: SecretKey,
}

pub struct BasicSigner {
    secp: Secp256k1<All>,
    keys: HashMap<String, KeyPair>,
}

impl BasicSigner {
    #[cfg(test)]
    pub fn new() -> VdrResult<BasicSigner> {
        Ok(BasicSigner {
            secp: Secp256k1::new(),
            keys: HashMap::new(),
        })
    }

    #[cfg(test)]
    pub fn add_key(&mut self, private_key: &str) -> VdrResult<()> {
        let private_key = SecretKey::from_str(private_key)?;
        let public_key = PublicKey::from_secret_key(&self.secp, &private_key);
        let address = self.get_address(&public_key);

        self.keys.insert(
            address,
            KeyPair {
                public_key,
                private_key,
            },
        );
        Ok(())
    }

    fn get_key(&self, account: &str) -> VdrResult<&KeyPair> {
        self.keys.get(account).ok_or(VdrError::SignerMissingKey(account.to_string()))
    }

    #[cfg(test)]
    fn get_address(&self, public_key: &PublicKey) -> String {
        let hash = keccak256(&public_key.serialize_uncompressed()[1..]);
        format!("0x{}", hex::encode(&hash[12..]))
    }
}

impl Signer for BasicSigner {
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<(RecoveryId, Vec<u8>)> {
        let key = self.get_key(account)?;
        let message = Message::from_slice(message)?;
        let (recovery_id, signature) = self
            .secp
            .sign_ecdsa_recoverable(&message, &key.private_key)
            .serialize_compact();
        Ok((recovery_id, signature.to_vec()))
    }

    fn has_key(&self, account: &str) -> bool {
        self.keys.contains_key(account)
    }

    fn public_key(&self, account: &str) -> Vec<u8> {
        match self.keys.get(account) {
            Some(key) => key.public_key.serialize_uncompressed().to_vec(),
            None => Vec::new(),
        }
    }
}

#[cfg(test)]
pub mod test {
    use super::*;

    pub const ACCOUNT: &'static str = "0xf0e2db6c8dc6c681bb5d6ad121a107f300e9b2b5";
    pub const PRIVATE_KEY: &'static str =
        "8bbbb1b345af56b560a5b20bd4b0ed1cd8cc9958a16262bc75118453cb546df7";

    pub fn signer() -> BasicSigner {
        let mut signer = BasicSigner::new().unwrap();
        signer.add_key(PRIVATE_KEY).unwrap();
        signer
    }

    #[test]
    fn add_key_test() {
        let basic_signer = signer();
        assert!(basic_signer.has_key(ACCOUNT));
    }
}
