use crate::{
    client::{
        ContractParam, LedgerClient, Transaction, TransactionBuilder, TransactionParser,
        TransactionType,
    },
    contracts::auth::{HasRole, Role},
    error::VdrResult,
};

pub struct RoleControl;

impl RoleControl {
    const CONTRACT_NAME: &'static str = "RoleControl";
    const METHOD_ASSIGN_ROLE: &'static str = "assignRole";
    const METHOD_REVOKE_ROLE: &'static str = "revokeRole";
    const METHOD_HAS_ROLE: &'static str = "hasRole";
    const METHOD_GET_ROLE: &'static str = "getRole";

    pub fn build_assign_role_transaction(
        client: &LedgerClient,
        from: &str,
        role: &Role,
        account: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_ASSIGN_ROLE)
            .add_param(role.into())
            .add_param(ContractParam::String(account.into()))
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(&client)
    }

    pub fn build_revoke_role_transaction(
        client: &LedgerClient,
        from: &str,
        role: &Role,
        account: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_REVOKE_ROLE)
            .add_param(role.into())
            .add_param(ContractParam::String(account.into()))
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(&client)
    }

    pub fn build_has_role_transaction(
        client: &LedgerClient,
        role: &Role,
        account: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_HAS_ROLE)
            .add_param(role.into())
            .add_param(ContractParam::String(account.into()))
            .set_type(TransactionType::Read)
            .build(&client)
    }

    pub fn build_get_role_transaction(
        client: &LedgerClient,
        account: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_ROLE)
            .add_param(ContractParam::String(account.into()))
            .set_type(TransactionType::Read)
            .build(&client)
    }

    pub fn parse_has_role_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<bool> {
        TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_HAS_ROLE)
            .parse::<HasRole>(&client, bytes)
    }

    pub fn parse_get_role_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<Role> {
        TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_HAS_ROLE)
            .parse::<Role>(&client, bytes)
    }

    pub async fn assign_role(
        client: &LedgerClient,
        from: &str,
        role: &Role,
        account: &str,
    ) -> VdrResult<String> {
        let transaction = Self::build_assign_role_transaction(client, from, role, account)?;
        client.sign_and_submit(&transaction).await
    }

    pub async fn revoke_role(
        client: &LedgerClient,
        from: &str,
        role: &Role,
        account: &str,
    ) -> VdrResult<String> {
        let transaction = Self::build_revoke_role_transaction(client, from, role, account)?;
        client.sign_and_submit(&transaction).await
    }

    pub async fn has_role(client: &LedgerClient, role: &Role, account: &str) -> VdrResult<bool> {
        let transaction = Self::build_has_role_transaction(client, role, account)?;
        let result = client.submit_transaction(&transaction).await?;
        Self::parse_has_role_result(client, &result)
    }

    pub async fn get_role(client: &LedgerClient, account: &str) -> VdrResult<Role> {
        let transaction = Self::build_get_role_transaction(client, account)?;
        let result = client.submit_transaction(&transaction).await?;
        Self::parse_get_role_result(client, &result)
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
}
