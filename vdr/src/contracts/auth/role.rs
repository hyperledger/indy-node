use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};

#[repr(u8)]
#[derive(Clone, PartialEq, Debug)]
pub enum Role {
    Empty = 0,
    Trustee = 1,
    Endorser = 2,
    Steward = 3,
}

pub type HasRole = bool;
pub type RoleIndex = u8;

impl Into<ContractParam> for Role {
    fn into(self) -> ContractParam {
        let role_index: RoleIndex = self.into();
        ContractParam::Uint(role_index.into())
    }
}

impl TryFrom<ContractOutput> for Role {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let role_index = value.get_u8(0)?;
        let role = Role::try_from(role_index)?;
        Ok(role)
    }
}

impl Into<RoleIndex> for Role {
    fn into(self) -> RoleIndex {
        self as u8
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
            _ => Err(VdrError::ContractInvalidResponseData(
                "Invalid role provided".to_string(),
            )),
        }
    }
}

impl TryFrom<ContractOutput> for HasRole {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        let has_role = value.get_bool(0)?;
        Ok(has_role)
    }
}
