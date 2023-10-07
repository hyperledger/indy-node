use crate::signer::Signer;

use web3::{
    ethabi::Address,
    signing::{keccak256, Key, Signature, SigningError},
    types::H256,
};

pub struct Web3Signer<'a> {
    account: String,
    signer: &'a Box<dyn Signer + 'static + Send + Sync>,
}

impl<'a> Web3Signer<'a> {
    pub fn new(
        account: String,
        signer: &'a Box<dyn Signer + 'static + Send + Sync>,
    ) -> Web3Signer<'a> {
        Web3Signer { account, signer }
    }
}

impl<'a> Key for Web3Signer<'a> {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let (recovery_id, signature) = self.signer.sign(message, &self.account)
            .map_err(|_| SigningError::InvalidMessage)?;

        let standard_v = recovery_id.to_i32() as u64;
        let v = match chain_id {
            Some(chain_id) => standard_v + 35 + chain_id * 2,
            None => standard_v + 27
        };
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let (recovery_id, signature) = self.signer.sign(message, &self.account)
            .map_err(|_| SigningError::InvalidMessage)?;

        let v = recovery_id.to_i32() as u64;
        let r = H256::from_slice(&signature[..32]);
        let s = H256::from_slice(&signature[32..]);

        Ok(Signature { v, r, s })
    }

    fn address(&self) -> Address {
        let public_key = self.signer.public_key(&self.account);
        let hash = keccak256(&public_key[1..]);
        Address::from_slice(&hash[12..])
    }
}
