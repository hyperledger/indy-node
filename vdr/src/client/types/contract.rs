use crate::error::{VdrError, VdrResult};

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

#[derive(Debug)]
pub struct ContractOutput(Vec<ContractParam>);

impl ContractOutput {
    pub fn new(data: Vec<ContractParam>) -> ContractOutput {
        ContractOutput(data)
    }

    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    pub fn size(&self) -> usize {
        self.0.len()
    }

    pub fn into_iter(self) -> impl Iterator<Item = ContractParam> {
        self.0.into_iter()
    }

    pub fn get_tuple(&self, index: usize) -> VdrResult<ContractOutput> {
        self.0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_tuple()
            .ok_or(VdrError::Unexpected)
            .map(|result| ContractOutput(result))
    }

    pub fn get_string(&self, index: usize) -> VdrResult<String> {
        self.0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_string()
            .ok_or(VdrError::Unexpected)
    }

    pub fn get_bool(&self, index: usize) -> VdrResult<bool> {
        self.0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_bool()
            .ok_or(VdrError::Unexpected)
    }

    pub fn get_u128(&self, index: usize) -> VdrResult<u128> {
        Ok(self
            .0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_uint()
            .ok_or(VdrError::Unexpected)?
            .as_u128())
    }

    pub fn get_string_array(&self, index: usize) -> VdrResult<Vec<String>> {
        self.0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_array()
            .ok_or(VdrError::Unexpected)?
            .into_iter()
            .map(|token| token.into_string().ok_or(VdrError::Unexpected))
            .collect()
    }

    pub fn get_objects_array(&self, index: usize) -> VdrResult<Vec<ContractOutput>> {
        let tokens = self
            .0
            .get(index)
            .ok_or(VdrError::Unexpected)?
            .clone()
            .into_array()
            .ok_or(VdrError::Unexpected)?;

        let mut result: Vec<ContractOutput> = Vec::new();
        for item in tokens.into_iter() {
            let item = item.into_tuple().ok_or(VdrError::Unexpected)?;
            result.push(ContractOutput(item))
        }
        Ok(result)
    }
}

impl From<Vec<Token>> for ContractOutput {
    fn from(value: Vec<Token>) -> Self {
        ContractOutput(value)
    }
}
