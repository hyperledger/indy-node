use log::trace;

use crate::{client::ContractOutput, error::VdrError, Address};

pub type ValidatorAddresses = Vec<Address>;

impl TryFrom<ContractOutput> for ValidatorAddresses {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!(
            "ValidatorAddresses convert from ContractOutput: {:?} has started",
            value
        );

        let validator_addresses = value.get_address_array(0);

        trace!(
            "ValidatorAddresses convert from ContractOutput has finished. Result: {:?}",
            validator_addresses
        );

        validator_addresses
    }
}
