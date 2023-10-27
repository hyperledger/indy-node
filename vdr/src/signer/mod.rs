#[cfg(any(feature = "basic_signer", test))]
pub mod basic_signer;

use crate::error::VdrResult;
use serde_derive::{Deserialize, Serialize};

#[cfg(any(feature = "basic_signer", test))]
pub use basic_signer::BasicSigner;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SignatureData {
    /// recovery ID using for public key recovery
    pub recovery_id: u64,
    /// ECDSA signature
    pub signature: Vec<u8>,
}

pub trait Signer: Send + Sync {
    /// Sign message using ECDSA with public key recoverability feature using the key associated with account
    ///
    /// # Params
    /// - `message` message to sign
    /// - `account` account to use for message signing
    ///
    /// # Returns
    /// signature data including recovery ID (for public key recovery) and ECDSA signature
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<SignatureData>;
}
