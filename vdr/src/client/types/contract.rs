use serde::Deserialize;
use web3::ethabi::Token;

#[derive(Debug, Default, PartialEq)]
pub struct ContractConfig {
    pub address: String,
    pub spec_path: String,
}

#[derive(Debug, Default, PartialEq, Deserialize)]
pub struct ContractSpec {
    #[serde(rename = "contractName")]
    pub name: String,
    pub abi: serde_json::Value,
}

pub type ContractParam = Token;
