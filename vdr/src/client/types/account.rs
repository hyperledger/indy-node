use crate::client::{ContractOutput, ContractParam};
use serde_derive::{Deserialize, Serialize};
use std::str::FromStr;

use crate::error::VdrError;
use web3::ethabi::ethereum_types::Address as Address_;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Address(String);

impl Address {
    pub fn new(address: &str) -> Address {
        Address(address.to_string())
    }

    pub fn value(&self) -> &str {
        &self.0
    }
}

impl TryInto<ContractParam> for Address {
    type Error = VdrError;

    fn try_into(self) -> Result<ContractParam, Self::Error> {
        let acc_address = Address_::from_str(self.value()).map_err(|err| {
            VdrError::CommonInvalidData(format!(
                "Unable to parse account address. Err: {:?}",
                err.to_string()
            ))
        })?;
        Ok(ContractParam::Address(acc_address))
    }
}

impl TryFrom<ContractOutput> for Address {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let account = value.get_string(0)?;
        Ok(Address(account))
    }
}
