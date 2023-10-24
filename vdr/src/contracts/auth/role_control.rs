use web3::types::U256;

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
            .add_param(ContractParam::Uint(U256::from(role.clone().into_index())))
            .add_param(ContractParam::Address(account.parse().unwrap()))
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
            .add_param(ContractParam::Uint(U256::from(role.clone().into_index())))
            .add_param(ContractParam::Address(account.parse().unwrap()))
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
            .add_param(ContractParam::Uint(U256::from(role.clone().into_index())))
            .add_param(ContractParam::Address(account.parse().unwrap()))
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
            .add_param(ContractParam::Address(account.parse().unwrap()))
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
            .set_method(Self::METHOD_GET_ROLE)
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
    use crate::{
        client::test::{client, CHAIN_ID, ROLE_CONTROL_ADDRESS},
        signer::test::ACCOUNT,
    };

    pub const NEW_ACCOUNT: &'static str = "0x0886328869e4e1f401e1052a5f4aae8b45f42610";

    mod build_assign_role_transaction {
        use super::*;

        #[test]
        fn build_assign_role_transaction_test() {
            let client = client();
            let expected_data = vec![
                136, 165, 191, 110, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50,
                136, 105, 228, 225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction = RoleControl::build_assign_role_transaction(
                &client,
                ACCOUNT,
                &Role::Trustee,
                NEW_ACCOUNT,
            )
            .unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
                to: ROLE_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data,
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_revoke_role_transaction {
        use super::*;

        #[test]
        fn build_revoke_role_transaction_test() {
            let client = client();
            let expected_data = vec![
                76, 187, 135, 211, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50,
                136, 105, 228, 225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction = RoleControl::build_revoke_role_transaction(
                &client,
                ACCOUNT,
                &Role::Trustee,
                NEW_ACCOUNT,
            )
            .unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
                to: ROLE_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data,
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_get_role_transaction {
        use super::*;

        #[test]
        fn build_get_role_transaction_test() {
            let client = client();
            let expected_data = vec![
                68, 39, 103, 51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 226, 219, 108, 141, 198,
                198, 129, 187, 93, 106, 209, 33, 161, 7, 243, 0, 233, 178, 181,
            ];

            let transaction = RoleControl::build_get_role_transaction(&client, ACCOUNT).unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Read,
                from: None,
                to: ROLE_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data,
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_get_role_result {
        use super::*;

        #[test]
        fn parse_get_role_result_test() {
            let client = client();
            let result = vec![0; 32];
            let expected_role = Role::Empty;

            let role = RoleControl::parse_get_role_result(&client, &result).unwrap();

            assert_eq!(expected_role, role);
        }
    }

    mod build_has_role_transaction {
        use super::*;

        #[test]
        fn build_has_role_transaction_test() {
            let client = client();
            let expected_data = vec![
                158, 151, 184, 246, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 226, 219,
                108, 141, 198, 198, 129, 187, 93, 106, 209, 33, 161, 7, 243, 0, 233, 178, 181,
            ];

            let transaction =
                RoleControl::build_has_role_transaction(&client, &Role::Trustee, ACCOUNT).unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Read,
                from: None,
                to: ROLE_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data,
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_has_role_result {
        use super::*;

        #[test]
        fn parse_has_role_result_test() {
            let client = client();
            let result = vec![0; 32];
            let expected_has_role = false;

            let has_role = RoleControl::parse_has_role_result(&client, &result).unwrap();

            assert_eq!(expected_has_role, has_role);
        }
    }
}
