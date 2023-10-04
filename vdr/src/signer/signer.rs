use crate::error::VdrResult;
use secp256k1::{ecdsa::RecoveryId, All, Message, PublicKey, Secp256k1, SecretKey};
use std::str::FromStr;

pub trait Signer {
    fn sign(&self, message: &[u8]) -> VdrResult<(RecoveryId, [u8; 64])>;
    fn public_key(&self) -> &PublicKey;
}

pub struct BasicSigner {
    secp: Secp256k1<All>,
    public_key: PublicKey,
    private_key: SecretKey,
}

impl BasicSigner {
    pub fn new(private_key: &str) -> VdrResult<BasicSigner> {
        let secp = Secp256k1::new();
        let private_key = SecretKey::from_str(private_key)?;
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        Ok(BasicSigner {
            secp: Secp256k1::new(),
            public_key,
            private_key,
        })
    }
}

impl Signer for BasicSigner {
    fn sign(&self, message: &[u8]) -> VdrResult<(RecoveryId, [u8; 64])> {
        let message = Message::from_slice(message)?;
        let (recovery_id, signature) = self
            .secp
            .sign_ecdsa_recoverable(&message, &self.private_key)
            .serialize_compact();
        Ok((recovery_id, signature))
    }

    fn public_key(&self) -> &PublicKey {
        &self.public_key
    }
}
