use crate::signer::Signer;
use web3::{
    ethabi::Address,
    signing::{keccak256, Key, Signature, SigningError},
    types::H256,
};

pub struct Web3Signer {
    secp_signer: Box<dyn Signer + 'static + Send + Sync>,
}

impl Web3Signer {
    pub fn new(signer: Box<dyn Signer + 'static + Send + Sync>) -> Web3Signer {
        Web3Signer {
            secp_signer: signer,
        }
    }
}

impl Key for &Web3Signer {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let (recovery_id, signature) = self.secp_signer.sign(message).unwrap();

        // FIXME: taken from web3
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
        let (recovery_id, signature) = self.secp_signer.sign(message).unwrap();

        // FIXME: taken from web3
        let v = recovery_id.to_i32() as u64;
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn address(&self) -> Address {
        let public_key = self.secp_signer.public_key().serialize_uncompressed();
        let hash = keccak256(&public_key[1..]);
        Address::from_slice(&hash[12..])
    }
}
