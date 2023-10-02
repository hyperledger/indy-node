use secp256k1::{All, Message, PublicKey, Secp256k1, SecretKey};
use std::str::FromStr;
use web3::{
    ethabi::Address,
    signing::{keccak256, Key, Signature, SigningError},
    types::H256,
};

pub struct Signer {
    secp: Secp256k1<All>,
    public_key: PublicKey,
    private_key: SecretKey,
}

impl Signer {
    pub fn new() -> Signer {
        let secp = Secp256k1::new();
        let private_key =
            SecretKey::from_str("8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63")
                .unwrap();
        let public_key = PublicKey::from_secret_key(&secp, &private_key);
        return Signer {
            secp: Secp256k1::new(),
            public_key,
            private_key,
        };
    }
}

impl Key for &Signer {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let message = Message::from_slice(message).map_err(|_| SigningError::InvalidMessage)?;
        let (recovery_id, signature) = self
            .secp
            .sign_ecdsa_recoverable(&message, &self.private_key)
            .serialize_compact();

        let standard_v = recovery_id.to_i32() as u64;
        let v = if let Some(chain_id) = chain_id {
            // When signing with a chain ID, add chain replay protection.
            standard_v + 35 + chain_id * 2
        } else {
            // Otherwise, convert to 'Electrum' notation.
            standard_v + 27
        };
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let message = Message::from_slice(message).map_err(|_| SigningError::InvalidMessage)?;
        let (recovery_id, signature) = self
            .secp
            .sign_ecdsa_recoverable(&message, &self.private_key)
            .serialize_compact();

        let v = recovery_id.to_i32() as u64;
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn address(&self) -> web3::types::Address {
        let public_key = self.public_key.serialize_uncompressed();
        let hash = keccak256(&public_key[1..]);
        Address::from_slice(&hash[12..])
    }
}
