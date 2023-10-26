use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};

#[derive(Clone, PartialEq, Debug, Copy)]
pub enum Role {
    Empty,
    Trustee,
    Endorser,
    Steward,
}

pub type HasRole = bool;
pub type RoleIndex = u8;

impl Into<ContractParam> for Role {
    fn into(self) -> ContractParam {
        let role_index: RoleIndex = Role::into(self);
        ContractParam::Uint(role_index.into())
    }
}

impl TryFrom<ContractOutput> for Role {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let role_index = value.get_u8(0).map_err(|_err| VdrError::Unexpected)?;

        let role = Role::try_from(role_index)?;

        Ok(role)
    }
}

impl Into<RoleIndex> for Role {
    fn into(self) -> RoleIndex {
        match self {
            Role::Empty => 0,
            Role::Trustee => 1,
            Role::Endorser => 2,
            Role::Steward => 3,
        }
    }
}

impl TryFrom<RoleIndex> for Role {
    type Error = VdrError;

    fn try_from(index: RoleIndex) -> Result<Self, Self::Error> {
        match index {
            0 => Ok(Role::Empty),
            1 => Ok(Role::Trustee),
            2 => Ok(Role::Endorser),
            3 => Ok(Role::Steward),
            _ => Err(VdrError::Unexpected),
        }
    }
}

impl TryFrom<ContractOutput> for HasRole {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let has_role = value.get_bool(0).map_err(|_err| VdrError::Unexpected)?;

        Ok(has_role)
    }
}
