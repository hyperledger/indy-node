use crate::signer::Signer;
use std::str::FromStr;

use crate::client::Address;
use web3::{
    ethabi::Address as EtabiAddress,
    signing::{Key, Signature, SigningError},
    types::H256,
};

/// TODO: Transaction signing is quite trick as it does payload/signature encoding
///  Rust Web3 crate does not expose `encode` functions, instead we have to implement the interface bellow
pub struct Web3Signer<'a> {
    account: Address,
    signer: &'a Box<dyn Signer>,
}

impl<'a> Web3Signer<'a> {
    pub fn new(account: Address, signer: &'a Box<dyn Signer>) -> Web3Signer<'a> {
        Web3Signer { account, signer }
    }
}

/// This implementation mostly borrowed from web3 signing module
impl<'a> Key for Web3Signer<'a> {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let signature_data = self
            .signer
            .sign(message, &self.account.value())
            .map_err(|_| SigningError::InvalidMessage)?;

        let v = match chain_id {
            Some(chain_id) => signature_data.recovery_id as u64 + 35 + chain_id * 2,
            None => signature_data.recovery_id as u64 + 27,
        };

        Ok(Signature {
            v,
            r: H256::from_slice(&signature_data.signature[..32]),
            s: H256::from_slice(&signature_data.signature[32..]),
        })
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let signature_data = self
            .signer
            .sign(message, &self.account.value())
            .map_err(|_| SigningError::InvalidMessage)?;

        Ok(Signature {
            v: signature_data.recovery_id as u64,
            r: H256::from_slice(&signature_data.signature[..32]),
            s: H256::from_slice(&signature_data.signature[32..]),
        })
    }

    fn address(&self) -> EtabiAddress {
        EtabiAddress::from_str(&self.account.value()).unwrap_or_default()
    }
}
