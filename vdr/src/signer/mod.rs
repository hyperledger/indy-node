pub mod signer;

use crate::error::VdrResult;

pub use signer::BasicSigner;

pub trait Signer {
    /// Sign message with the key associated with account
    ///
    /// # Params
    /// - `message` message to sign
    /// - `account` account to use for message signing
    ///
    /// # Returns
    /// recovery ID (for public key recovery) and ECDSA signature
    fn sign(&self, message: &[u8], account: &str) -> VdrResult<(i32, Vec<u8>)>;
}
