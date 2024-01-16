use crate::client::{ContractOutput, ContractParam};
use log::trace;
use serde_derive::{Deserialize, Serialize};
use std::str::FromStr;

use crate::error::VdrError;
use web3::ethabi::ethereum_types::Address as Address_;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Address(String);

impl Address {
    pub fn new(address: &str) -> Address {
        if address.starts_with("0x") {
            Address(address.to_string())
        } else {
            Address(format!("0x{}", address))
        }
    }

    pub fn value(&self) -> &str {
        &self.0
    }
}

impl TryInto<ContractParam> for Address {
    type Error = VdrError;

    fn try_into(self) -> Result<ContractParam, Self::Error> {
        trace!("Address: {:?} convert into ContractParam has started", self);

        let acc_address = Address_::from_str(self.value()).map_err(|err| {
            VdrError::CommonInvalidData(format!(
                "Unable to parse account address. Err: {:?}",
                err.to_string()
            ))
        })?;

        let acc_address_contract_param = ContractParam::Address(acc_address);

        trace!(
            "Address: {:?} convert into ContractParam has finished. Result: {:?}",
            self,
            acc_address_contract_param
        );

        Ok(ContractParam::Address(acc_address))
    }
}

impl TryFrom<ContractOutput> for Address {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!(
            "Address convert from ContractOutput: {:?} has started",
            value
        );

        let acc_address = Address(value.get_string(0)?);

        trace!(
            "Address convert from ContractOutput: {:?} has finished. Result: {:?}",
            value,
            acc_address
        );

        Ok(acc_address)
    }
}
