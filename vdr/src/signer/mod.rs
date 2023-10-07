mod signer;

use crate::error::VdrResult;
use secp256k1::ecdsa::RecoveryId;

pub use signer::BasicSigner;

pub trait Signer {
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<(RecoveryId, Vec<u8>)>;
    fn contain_key(&self, account: &str) -> bool;
    fn public_key(&self, account: &str) -> Vec<u8>;
}
