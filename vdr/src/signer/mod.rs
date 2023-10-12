mod signer;

use crate::error::VdrResult;
use secp256k1::ecdsa::RecoveryId;

#[cfg(test)]
pub use signer::{test, BasicSigner};

pub trait Signer {
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<(RecoveryId, Vec<u8>)>;
    fn has_key(&self, account: &str) -> bool;
    fn public_key(&self, account: &str) -> Vec<u8>;
}
