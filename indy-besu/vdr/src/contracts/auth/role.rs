use log::{debug, trace};

use crate::{
    client::{ContractOutput, ContractParam},
    error::VdrError,
};

#[repr(u8)]
#[derive(Clone, Copy, PartialEq, Debug)]
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
        trace!("Role: {:?} convert to ContractParam started", self);

        let role_index: RoleIndex = self.into();
        let role_contract_param = ContractParam::Uint(role_index.into());

        debug!(
            "Role: {:?} convert to ContractParam finished. Result: {:?}",
            self, role_contract_param
        );

        role_contract_param
    }
}

impl TryFrom<ContractOutput> for Role {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!("Role convert from ContractOutput: {:?} started", value);

        let role_index = value.get_u8(0)?;
        let role = Role::try_from(role_index)?;

        debug!(
            "Role convert from ContractOutput: {:?} finished. Result: {:?}",
            value, role
        );

        Ok(role)
    }
}

impl Into<RoleIndex> for Role {
    fn into(self) -> RoleIndex {
        trace!("Role: {:?} convert to RoleIndex started", self);

        let role_index = self as u8;

        debug!(
            "Role: {:?} convert to RoleIndex finished. Result: {}",
            self, role_index
        );

        role_index
    }
}

impl TryFrom<RoleIndex> for Role {
    type Error = VdrError;

    fn try_from(index: RoleIndex) -> Result<Self, Self::Error> {
        trace!("RoleIndex: {} convert to Role started", index);

        let result = match index {
            0 => Ok(Role::Empty),
            1 => Ok(Role::Trustee),
            2 => Ok(Role::Endorser),
            3 => Ok(Role::Steward),
            _ => Err(VdrError::ContractInvalidResponseData(
                "Invalid role provided".to_string(),
            )),
        };

        debug!(
            "RoleIndex: {} convert to Role started. Result: {:?}",
            index, result
        );

        result
    }
}

impl TryFrom<ContractOutput> for HasRole {
    type Error = VdrError;

    fn try_from(value: ContractOutput) -> Result<Self, Self::Error> {
        trace!("ContractOutput: {:?} convert to HasRole started", value);

        let has_role = value.get_bool(0)?;

        debug!(
            "ContractOutput: {:?} convert to HasRole finished. Result: {}",
            value, has_role
        );

        Ok(has_role)
    }
}
