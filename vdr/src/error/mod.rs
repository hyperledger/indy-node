use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum VdrError {
    #[error("Bla")]
    Unexpected,

    #[error("Common error")]
    Common(String),

    #[error("web3 error")]
    Web3(String),
}

pub type VdrResult<T> = Result<T, VdrError>;

impl From<web3::Error> for VdrError {
    fn from(value: web3::Error) -> Self {
        VdrError::Web3(value.to_string())
    }
}

impl From<web3::ethabi::Error> for VdrError {
    fn from(value: web3::ethabi::Error) -> Self {
        VdrError::Web3(value.to_string())
    }
}

impl From<std::io::Error> for VdrError {
    fn from(_value: std::io::Error) -> Self {
        VdrError::Unexpected
    }
}

impl From<secp256k1::Error> for VdrError {
    fn from(_value: secp256k1::Error) -> Self {
        VdrError::Unexpected
    }
}
