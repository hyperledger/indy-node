use crate::error::{VdrError, VdrResult};

use crate::Address;
use log::{trace, warn};
use serde::{Deserialize, Serialize};
use web3::ethabi::Token;

/// Contract configuration
#[derive(Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct ContractConfig {
    /// Address of deployed contract
    pub address: String,
    /// Contract ABI specification
    pub spec_path: String,
}

/// Contract ABI specification
#[derive(Debug, Default, PartialEq, Deserialize)]
pub struct ContractSpec {
    /// Name of contract
    #[serde(rename = "contractName")]
    pub name: String,
    /// Contract ABI itself
    pub abi: serde_json::Value,
}

impl ContractSpec {
    /// Read and parse contract specification from a JSON file
    pub fn from_file(spec_path: &str) -> VdrResult<Self> {
        let contract_spec = std::fs::read_to_string(spec_path).map_err(|err| {
            let vdr_error = VdrError::ContractInvalidSpec(format!(
                "Unable to read contract spec file. Err: {:?}",
                err
            ));

            warn!(
                "Error: {:?} during reading contract spec from file",
                vdr_error
            );

            vdr_error
        })?;
        let contract_spec = serde_json::from_str(&contract_spec).map_err(|err| {
            let vdr_error = VdrError::ContractInvalidSpec(format!(
                "Unable to parse contract specification. Err: {:?}",
                err.to_string()
            ));

            warn!(
                "Error: {:?} during paring contract specification",
                vdr_error
            );

            vdr_error
        });

        trace!(
            "Read contract specification from file. Result: {:?}",
            contract_spec
        );

        contract_spec
    }
}

/// Contract parameters representation (ethereum ABI)
pub type ContractParam = Token;

/// Helper wrapper for more convenient parsing of the contract execution results
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
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing tuple value".to_string())
            })?
            .clone()
            .into_tuple()
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing tuple value".to_string()))
            .map(ContractOutput)
    }

    pub fn get_string(&self, index: usize) -> VdrResult<String> {
        self.0
            .get(index)
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing string value".to_string())
            })?
            .clone()
            .into_string()
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing string value".to_string())
            })
    }

    pub fn get_address(&self, index: usize) -> VdrResult<Address> {
        let address_str = self
            .0
            .get(index)
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing address value".to_string())
            })?
            .clone()
            .to_string();

        Ok(Address::new(&address_str))
    }

    pub fn get_bool(&self, index: usize) -> VdrResult<bool> {
        self.0
            .get(index)
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing bool value".to_string()))?
            .clone()
            .into_bool()
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing bool value".to_string()))
    }

    pub fn get_u128(&self, index: usize) -> VdrResult<u128> {
        Ok(self
            .0
            .get(index)
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing uint value".to_string()))?
            .clone()
            .into_uint()
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing uint value".to_string()))?
            .as_u128())
    }

    pub fn get_u8(&self, index: usize) -> VdrResult<u8> {
        Ok(self
            .0
            .get(index)
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing uint value".to_string()))?
            .clone()
            .into_uint()
            .ok_or_else(|| VdrError::ContractInvalidResponseData("Missing uint value".to_string()))?
            .as_u32() as u8)
    }

    pub fn get_string_array(&self, index: usize) -> VdrResult<Vec<String>> {
        self.0
            .get(index)
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing string array value".to_string())
            })?
            .clone()
            .into_array()
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing string array value".to_string())
            })?
            .into_iter()
            .map(|token| {
                token.into_string().ok_or_else(|| {
                    VdrError::ContractInvalidResponseData("Missing string value".to_string())
                })
            })
            .collect()
    }

    pub fn get_address_array(&self, index: usize) -> VdrResult<Vec<Address>> {
        Ok(self
            .0
            .get(index)
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData(
                    "Missing address string array value".to_string(),
                )
            })?
            .clone()
            .into_array()
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData(
                    "Missing address string array value".to_string(),
                )
            })?
            .into_iter()
            .map(|token| Address::new(&token.to_string()))
            .collect())
    }

    pub fn get_objects_array(&self, index: usize) -> VdrResult<Vec<ContractOutput>> {
        let tokens = self
            .0
            .get(index)
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing object array value".to_string())
            })?
            .clone()
            .into_array()
            .ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing object array value".to_string())
            })?;

        let mut result: Vec<ContractOutput> = Vec::new();
        for item in tokens.into_iter() {
            let item = item.into_tuple().ok_or_else(|| {
                VdrError::ContractInvalidResponseData("Missing object value".to_string())
            })?;
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
