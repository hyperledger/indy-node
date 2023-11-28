use crate::{
    client::{
        Address, LedgerClient, Transaction, TransactionBuilder, TransactionParser, TransactionType,
    },
    contracts::auth::{HasRole, Role},
    error::VdrResult,
};
use log::{debug, info};

/// RoleControl contract methods
pub struct RoleControl;

impl RoleControl {
    const CONTRACT_NAME: &'static str = "RoleControl";
    const METHOD_ASSIGN_ROLE: &'static str = "assignRole";
    const METHOD_REVOKE_ROLE: &'static str = "revokeRole";
    const METHOD_HAS_ROLE: &'static str = "hasRole";
    const METHOD_GET_ROLE: &'static str = "getRole";

    /// Build transaction to execute RoleControl.assignRole contract method to assign a role to an account
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `role` role to assign
    /// - `account` assignee account
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_assign_role_transaction(
        client: &LedgerClient,
        from: &Address,
        role: &Role,
        account: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, assignee: {}, role: {:?}",
            Self::METHOD_ASSIGN_ROLE,
            from.value(),
            account.value(),
            role
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_ASSIGN_ROLE)
            .add_param((*role).into())
            .add_param(account.clone().try_into()?)
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_ASSIGN_ROLE,
            transaction
        );

        transaction
    }

    /// Build transaction to execute RoleControl.revokeRole contract method to revoke a role from an account
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `role` role to assign
    /// - `account` revokee account
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_revoke_role_transaction(
        client: &LedgerClient,
        from: &Address,
        role: &Role,
        account: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, revokee: {}, role: {:?}",
            Self::METHOD_REVOKE_ROLE,
            from.value(),
            account.value(),
            role
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_REVOKE_ROLE)
            .add_param((*role).into())
            .add_param(account.clone().try_into()?)
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_REVOKE_ROLE,
            transaction
        );

        transaction
    }

    /// Build transaction to execute RoleControl.hasRole contract method to check an account has a role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `role` role to check
    /// - `account` account to check
    ///
    /// # Returns
    /// Read transaction to submit
    pub fn build_has_role_transaction(
        client: &LedgerClient,
        role: &Role,
        account: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Account to check: {}, role: {:?}",
            Self::METHOD_HAS_ROLE,
            account.value(),
            role
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_HAS_ROLE)
            .add_param((*role).into())
            .add_param(account.clone().try_into()?)
            .set_type(TransactionType::Read)
            .build(client);

        info!(
            "{} txn build has finished. Result {:?}",
            Self::METHOD_HAS_ROLE,
            transaction
        );

        transaction
    }

    /// Build transaction to execute RoleControl.getRole contract method to get account's role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `account` account address
    ///
    /// # Returns
    /// Read transaction to submit
    pub fn build_get_role_transaction(
        client: &LedgerClient,
        account: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Account to get: {}",
            Self::METHOD_GET_ROLE,
            account.value(),
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_ROLE)
            .add_param(account.clone().try_into()?)
            .set_type(TransactionType::Read)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_GET_ROLE,
            transaction
        );

        transaction
    }

    /// Parse the result of execution RoleControl.HasRole contract method to check an account has a role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `bytes` result bytes returned from the ledger
    ///
    /// # Returns
    /// Account has role result
    pub fn parse_has_role_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<bool> {
        debug!(
            "{} result parse has started. Bytes to parse: {:?}",
            Self::METHOD_HAS_ROLE,
            bytes
        );

        let parse_result = TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_HAS_ROLE)
            .parse::<HasRole>(client, bytes);

        info!(
            "{} result parse has finished. Result: {:?}",
            Self::METHOD_HAS_ROLE,
            parse_result
        );

        parse_result
    }

    /// Parse the result of execution RoleControl.GetRole contract method to get account's role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `bytes` result bytes returned from the ledger
    ///
    /// # Returns
    /// Account's role
    pub fn parse_get_role_result(client: &LedgerClient, bytes: &[u8]) -> VdrResult<Role> {
        debug!(
            "{} result parse has started. Bytes to parse: {:?}",
            Self::METHOD_GET_ROLE,
            bytes
        );

        let parse_result = TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_ROLE)
            .parse::<Role>(client, bytes);

        info!(
            "{} result parse has finished. Result: {:?}",
            Self::METHOD_GET_ROLE,
            parse_result
        );

        parse_result
    }

    /// Single step function executing RoleControl.assignRole contract method to assign a role to an account
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `role` role to assign
    /// - `account` assignee account
    ///
    /// # Returns
    /// Receipt of executed transaction
    pub async fn assign_role(
        client: &LedgerClient,
        from: &Address,
        role: &Role,
        account: &Address,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Assigner: {:?}, Assignee: {:?}, Role: {:?}",
            Self::METHOD_ASSIGN_ROLE,
            from,
            account,
            role
        );

        let transaction = Self::build_assign_role_transaction(client, from, role, account)?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_ASSIGN_ROLE,
            receipt
        );

        receipt
    }

    /// Single step function executing RoleControl.revokeRole contract method to revoke a role from an account
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `role` role to assign
    /// - `account` revokee account
    ///
    /// # Returns
    /// Receipt of executed transaction
    pub async fn revoke_role(
        client: &LedgerClient,
        from: &Address,
        role: &Role,
        account: &Address,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Revoker: {:?}, Revokee: {:?}, Role: {:?}",
            Self::METHOD_REVOKE_ROLE,
            from,
            account,
            role
        );

        let transaction = Self::build_revoke_role_transaction(client, from, role, account)?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_REVOKE_ROLE,
            receipt
        );

        receipt
    }

    /// Single step function executing RoleControl.hasRole contract method to check an account has a role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `role` role to check
    /// - `account` account to check
    ///
    /// # Returns
    /// Account has role result
    pub async fn has_role(
        client: &LedgerClient,
        role: &Role,
        account: &Address,
    ) -> VdrResult<bool> {
        debug!(
            "{} check has started. Account: {:?}, Role: {:?}",
            Self::METHOD_HAS_ROLE,
            account,
            role
        );

        let transaction = Self::build_has_role_transaction(client, role, account)?;
        let result = client.submit_transaction(&transaction).await?;
        let parsed_result = Self::parse_has_role_result(client, &result);

        info!(
            "{} check has finished. Result: {:?}",
            Self::METHOD_HAS_ROLE,
            parsed_result
        );

        parsed_result
    }

    /// Single step function executing RoleControl.getRole contract method to get account's role
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `account` account address
    ///
    /// # Returns
    /// Account's role
    pub async fn get_role(client: &LedgerClient, account: &Address) -> VdrResult<Role> {
        debug!(
            "{} process has started. Account: {:?}",
            Self::METHOD_GET_ROLE,
            account
        );

        let transaction = Self::build_get_role_transaction(client, account)?;
        let result = client.submit_transaction(&transaction).await?;
        let parsed_result = Self::parse_get_role_result(client, &result);

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_GET_ROLE,
            parsed_result
        );

        parsed_result
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        client::test::{client, CHAIN_ID, ROLE_CONTROL_ADDRESS},
        signer::basic_signer::test::TRUSTEE_ACC,
        utils::init_env_logger,
    };

    pub const NEW_ACCOUNT: &str = "0x0886328869e4e1f401e1052a5f4aae8b45f42610";

    fn account() -> Address {
        Address::new(NEW_ACCOUNT)
    }

    mod build_assign_role_transaction {
        use super::*;

        #[test]
        fn build_assign_role_transaction_test() {
            init_env_logger();
            let client = client(None);
            let expected_data = vec![
                136, 165, 191, 110, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50,
                136, 105, 228, 225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction = RoleControl::build_assign_role_transaction(
                &client,
                &TRUSTEE_ACC,
                &Role::Trustee,
                &account(),
            )
            .unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
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
            init_env_logger();
            let client = client(None);
            let expected_data = vec![
                76, 187, 135, 211, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50,
                136, 105, 228, 225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction = RoleControl::build_revoke_role_transaction(
                &client,
                &TRUSTEE_ACC,
                &Role::Trustee,
                &account(),
            )
            .unwrap();

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
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
            init_env_logger();
            let client = client(None);
            let expected_data = vec![
                68, 39, 103, 51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50, 136, 105, 228,
                225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction = RoleControl::build_get_role_transaction(&client, &account()).unwrap();

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
            init_env_logger();
            let client = client(None);
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
            init_env_logger();
            let client = client(None);
            let expected_data = vec![
                158, 151, 184, 246, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 134, 50,
                136, 105, 228, 225, 244, 1, 225, 5, 42, 95, 74, 174, 139, 69, 244, 38, 16,
            ];

            let transaction =
                RoleControl::build_has_role_transaction(&client, &Role::Trustee, &account())
                    .unwrap();

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
            init_env_logger();
            let client = client(None);
            let result = vec![0; 32];
            let expected_has_role = false;

            let has_role = RoleControl::parse_has_role_result(&client, &result).unwrap();

            assert_eq!(expected_has_role, has_role);
        }
    }
}
