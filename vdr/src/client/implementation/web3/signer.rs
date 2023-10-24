use crate::signer::Signer;
use std::str::FromStr;

use web3::{
    ethabi::Address,
    signing::{Key, Signature, SigningError},
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
        let (recovery_id, signature) = self
            .signer
            .sign(message, &self.account)
            .map_err(|_| SigningError::InvalidMessage)?;

        let v = match chain_id {
            Some(chain_id) => recovery_id as u64 + 35 + chain_id * 2,
            None => recovery_id as u64 + 27,
        };

        Ok(Signature {
            v,
            r: H256::from_slice(&signature[..32]),
            s: H256::from_slice(&signature[32..]),
        })
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let (recovery_id, signature) = self
            .signer
            .sign(message, &self.account)
            .map_err(|_| SigningError::InvalidMessage)?;

        Ok(Signature {
            v: recovery_id as u64,
            r: H256::from_slice(&signature[..32]),
            s: H256::from_slice(&signature[32..]),
        })
    }

    fn address(&self) -> Address {
        Address::from_str(&self.account).unwrap_or_default()
    }
}
