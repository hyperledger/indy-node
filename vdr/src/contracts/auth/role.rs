use crate::{client::ContractOutput, error::VdrError};

pub enum Role {
    Empty,
    Trustee,
    Endorser,
    Steward,
}

pub type HasRole = bool;

impl Role {
    fn from_index(index: u128) -> Self {
        match index {
            0 => Role::Empty,
            1 => Role::Trustee,
            2 => Role::Endorser,
            3 => Role::Steward,
        }
    }
}

impl TryFrom<ContractOutput> for Role {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let role_index = value.get_u128(0).map_err(|_err| VdrError::Unexpected)?;

        let role = Role::from_index(role_index);

        Ok(role)
    }
}

impl TryFrom<ContractOutput> for HasRole {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let has_role = value.get_bool(0).map_err(|_err| VdrError::Unexpected)?;

        Ok(has_role)
    }
}
