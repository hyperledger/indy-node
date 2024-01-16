use crate::signer::Signer;
use std::str::FromStr;

use crate::client::Address;
use log::{trace, warn};
use web3::{
    ethabi::Address as EtabiAddress,
    signing::{Key, Signature, SigningError},
    types::H256,
};

/// TODO: Transaction signing is quite trick as it does payload/signature encoding
///  Rust Web3 crate does not expose `encode` functions, instead we have to implement the interface bellow
pub struct Web3Signer<'a> {
    account: Address,
    signer: &'a dyn Signer,
}

impl<'a> Web3Signer<'a> {
    pub fn new(account: Address, signer: &'a dyn Signer) -> Web3Signer<'a> {
        let signer = Web3Signer {
            account: account.clone(),
            signer,
        };

        trace!("Created new signer. Address: {:?}", account);

        signer
    }
}

/// This implementation mostly borrowed from web3 signing module
impl<'a> Key for Web3Signer<'a> {
    fn sign(&self, message: &[u8], chain_id: Option<u64>) -> Result<Signature, SigningError> {
        let signature_data = self
            .signer
            .sign(message, self.account.value())
            .map_err(|_| {
                let web3_err = SigningError::InvalidMessage;

                warn!("Error:{} during signing message: {:?}", web3_err, message);

                web3_err
            })?;

        let v = match chain_id {
            Some(chain_id) => signature_data.recovery_id + 35 + chain_id * 2,
            None => signature_data.recovery_id + 27,
        };

        let signature = Signature {
            v,
            r: H256::from_slice(&signature_data.signature[..32]),
            s: H256::from_slice(&signature_data.signature[32..]),
        };

        trace!("Signed message: {:?}", message);

        Ok(signature)
    }

    fn sign_message(&self, message: &[u8]) -> Result<Signature, SigningError> {
        let signature_data = self
            .signer
            .sign(message, self.account.value())
            .map_err(|_| SigningError::InvalidMessage)?;

        let signature = Signature {
            v: signature_data.recovery_id,
            r: H256::from_slice(&signature_data.signature[..32]),
            s: H256::from_slice(&signature_data.signature[32..]),
        };

        trace!("Signed message: {:?}", message);

        Ok(signature)
    }

    fn address(&self) -> EtabiAddress {
        EtabiAddress::from_str(self.account.value()).unwrap_or_default()
    }
}
