use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum VdrError {
    #[error("Ledger Client: Node is unreachable")]
    ClientNodeUnreachable,

    #[error("Ledger Client: Invalid transaction: {}", _0)]
    ClientInvalidTransaction(String),

    #[error("Ledger Client: Got invalid response: {}", _0)]
    ClientInvalidResponse(String),

    #[error("Ledger Client: Unexpected error occurred: {}", _0)]
    ClientUnexpectedError(String),

    #[error("Ledger Client: Invalid state {}", _0)]
    ClientInvalidState(String),

    #[error("Contract: Invalid name: {}", _0)]
    ContractInvalidName(String),

    #[error("Contract: Invalid specification: {}", _0)]
    ContractInvalidSpec(String),

    #[error("Contract: Invalid data")]
    ContractInvalidInputData,

    #[error("Contract: Invalid response data")]
    ContractInvalidResponseData,

    #[error("Signer: Invalid private key")]
    SignerInvalidPrivateKey,

    #[error("Signer: Invalid message")]
    SignerInvalidMessage,

    #[error("Signer: Key is missing: {}", _0)]
    SignerMissingKey(String),

    #[error("Signer: Unexpected error occurred")]
    SignerUnexpectedError,

    #[error("Invalid data: {}", _0)]
    CommonInvalidData(String),
}

pub type VdrResult<T> = Result<T, VdrError>;

impl From<web3::Error> for VdrError {
    fn from(value: web3::Error) -> Self {
        match value {
            web3::Error::Unreachable => VdrError::ClientNodeUnreachable,
            web3::Error::InvalidResponse(err) => VdrError::ClientInvalidResponse(err),
            _ => VdrError::ClientUnexpectedError(value.to_string()),
        }
    }
}

impl From<web3::ethabi::Error> for VdrError {
    fn from(value: web3::ethabi::Error) -> Self {
        match value {
            web3::ethabi::Error::InvalidName(name) => VdrError::ContractInvalidName(name),
            _ => VdrError::ContractInvalidInputData,
        }
    }
}

impl From<secp256k1::Error> for VdrError {
    fn from(value: secp256k1::Error) -> Self {
        match value {
            secp256k1::Error::InvalidPublicKey => VdrError::SignerInvalidPrivateKey,
            secp256k1::Error::InvalidMessage => VdrError::SignerInvalidMessage,
            _ => VdrError::SignerUnexpectedError,
        }
    }
}
