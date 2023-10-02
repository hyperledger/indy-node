mod transaction;

use web3::{
    ethabi::Token,
    types::{Address as Web3Address, Bytes as Web3Bytes, U256 as Web3U256, U64 as Web3U64},
};

pub use transaction::Transaction;

pub type U256 = Web3U256;
pub type U64 = Web3U64;
pub type Address = Web3Address;
pub type Bytes = Web3Bytes;
pub type ContractParam = Token;
