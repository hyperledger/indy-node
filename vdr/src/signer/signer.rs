use crate::{
    error::{VdrError, VdrResult},
    signer::Signer,
};

use secp256k1::{ecdsa::RecoveryId, All, Message, PublicKey, Secp256k1, SecretKey};
use std::{collections::HashMap, str::FromStr};

pub struct KeyPair {
    public_key: PublicKey,
    private_key: SecretKey,
}

pub struct BasicSigner {
    secp: Secp256k1<All>,
    keys: HashMap<String, KeyPair>,
}

impl BasicSigner {
    pub fn new() -> VdrResult<BasicSigner> {
        Ok(BasicSigner {
            secp: Secp256k1::new(),
            keys: HashMap::new(),
        })
    }

    pub fn add_key(&mut self, id: &str, private_key: &str) -> VdrResult<()> {
        let private_key = SecretKey::from_str(private_key)?;
        let public_key = PublicKey::from_secret_key(&self.secp, &private_key);
        self.keys.insert(
            id.to_string(),
            KeyPair {
                public_key,
                private_key,
            },
        );
        Ok(())
    }

    fn get_key(&self, account: &str) -> VdrResult<&KeyPair> {
        self.keys.get(account).ok_or(VdrError::Unexpected)
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

    fn contain_key(&self, account: &str) -> bool {
        self.keys.contains_key(account)
    }

    fn public_key(&self, account: &str) -> Vec<u8> {
        match self.keys.get(account) {
            Some(key) => key.public_key.serialize_uncompressed().to_vec(),
            None => Vec::new(),
        }
    }
}
