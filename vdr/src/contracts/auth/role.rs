use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};

#[derive(Clone, PartialEq, Debug)]
pub enum Role {
    Empty,
    Trustee,
    Endorser,
    Steward,
}

pub type HasRole = bool;

impl Role {
    fn from_index(index: u64) -> Self {
        match index {
            0 => Role::Empty,
            1 => Role::Trustee,
            2 => Role::Endorser,
            3 => Role::Steward,
            _ => Role::Empty,
        }
    }

    pub fn into_index(self) -> u64 {
        match self {
            Role::Empty => 0,
            Role::Trustee => 1,
            Role::Endorser => 2,
            Role::Steward => 3,
        }
    }
}

impl Into<ContractParam> for Role {
    fn into(self) -> ContractParam {
        ContractParam::Uint(self.into_index().into())
    }
}

impl TryFrom<ContractOutput> for Role {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let role_index = value.get_u64(0).map_err(|_err| VdrError::Unexpected)?;

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
