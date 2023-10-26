use crate::{client::ContractOutput, error::VdrError};

pub type ValidatorAddresses = Vec<String>;

impl TryFrom<ContractOutput> for ValidatorAddresses {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        value.get_address_string_array(0)
    }
}
