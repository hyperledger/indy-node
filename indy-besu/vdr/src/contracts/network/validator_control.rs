use log::{debug, info};

use crate::{
    client::{Transaction, TransactionBuilder, TransactionParser, TransactionType},
    error::VdrResult,
    Address, LedgerClient,
};

use super::validator_info::ValidatorAddresses;

/// ValidatorControl contract methods
pub struct ValidatorControl;

impl ValidatorControl {
    const CONTRACT_NAME: &'static str = "ValidatorControl";
    const METHOD_ADD_VALIDATOR: &'static str = "addValidator";
    const METHOD_REMOVE_VALIDATOR: &'static str = "removeValidator";
    const METHOD_GET_VALIDATORS: &'static str = "getValidators";

    /// Build transaction to execute ValidatorControl.addValidator contract method to add a new Validator
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `validator_address` validator address to be added
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_add_validator_transaction(
        client: &LedgerClient,
        from: &Address,
        validator_address: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, validator address: {}",
            Self::METHOD_ADD_VALIDATOR,
            from.value(),
            validator_address.value()
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_ADD_VALIDATOR)
            .add_param(validator_address.clone().try_into()?)
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_ADD_VALIDATOR,
            transaction
        );

        transaction
    }

    /// Build transaction to execute ValidatorControl.removeValidator contract method to remove an existing Validator
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `validator_address` validator address to be removed
    ///
    /// # Returns
    /// Write transaction to sign and submit
    pub fn build_remove_validator_transaction(
        client: &LedgerClient,
        from: &Address,
        validator_address: &Address,
    ) -> VdrResult<Transaction> {
        debug!(
            "{} txn build has started. Sender: {}, validator address: {}",
            Self::METHOD_REMOVE_VALIDATOR,
            from.value(),
            validator_address.value()
        );

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_REMOVE_VALIDATOR)
            .add_param(validator_address.clone().try_into()?)
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_REMOVE_VALIDATOR,
            transaction
        );

        transaction
    }

    /// Build transaction to execute ValidatorControl.getValidators contract method to get existing validators
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    ///
    /// # Returns
    /// Read transaction to submit
    pub fn build_get_validators_transaction(client: &LedgerClient) -> VdrResult<Transaction> {
        debug!("{} txn build has started", Self::METHOD_GET_VALIDATORS,);

        let transaction = TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_VALIDATORS)
            .set_type(TransactionType::Read)
            .build(client);

        info!(
            "{} txn build has finished. Result: {:?}",
            Self::METHOD_GET_VALIDATORS,
            transaction
        );

        transaction
    }

    /// Parse the result of execution ValidatorControl.getValidators contract method to get existing validators
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `bytes` result bytes returned from the ledger
    ///
    /// # Returns
    /// Parsed validator addresses
    pub fn parse_get_validators_result(
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<ValidatorAddresses> {
        debug!(
            "{} result parse has started. Bytes to parse: {:?}",
            Self::METHOD_GET_VALIDATORS,
            bytes
        );

        let result = TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_VALIDATORS)
            .parse::<ValidatorAddresses>(client, bytes);

        info!(
            "{} result parse has finished. Result: {:?}",
            Self::METHOD_GET_VALIDATORS,
            result
        );

        result
    }

    /// Single step function executing ValidatorControl.addValidator contract method to add a new Validator
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `validator_address` validator address to be added
    ///
    /// # Returns
    /// Receipt of executed transaction
    pub async fn add_validator(
        client: &LedgerClient,
        from: &Address,
        validator_address: &Address,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Sender: {}, validator address: {:?}",
            Self::METHOD_ADD_VALIDATOR,
            from.value(),
            validator_address
        );

        let transaction = Self::build_add_validator_transaction(client, from, validator_address)?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_ADD_VALIDATOR,
            receipt
        );

        receipt
    }

    /// Single step function executing ValidatorControl.removeValidator contract method to remove an existing Validator
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    /// - `from` transaction sender account address
    /// - `validator_address` validator address to be added
    ///
    /// # Returns
    /// Receipt of executed transaction
    pub async fn remove_validator(
        client: &LedgerClient,
        from: &Address,
        validator_address: &Address,
    ) -> VdrResult<String> {
        debug!(
            "{} process has started. Sender: {}, validator address: {:?}",
            Self::METHOD_REMOVE_VALIDATOR,
            from.value(),
            validator_address
        );

        let transaction =
            Self::build_remove_validator_transaction(client, from, validator_address)?;
        let receipt = client.sign_and_submit(&transaction).await;

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_REMOVE_VALIDATOR,
            receipt
        );

        receipt
    }

    /// Single step function executing ValidatorControl.getValidators contract method to get existing validators
    ///
    /// # Params
    /// - `client` client connected to the network where contract will be executed
    ///
    /// # Returns
    /// Existing validator addresses
    pub async fn get_validators(client: &LedgerClient) -> VdrResult<ValidatorAddresses> {
        debug!("{} process has started", Self::METHOD_GET_VALIDATORS,);

        let transaction = Self::build_get_validators_transaction(client)?;
        let result = client.submit_transaction(&transaction).await?;
        let parsed_result = Self::parse_get_validators_result(client, &result);

        info!(
            "{} process has finished. Result: {:?}",
            Self::METHOD_REMOVE_VALIDATOR,
            parsed_result
        );

        parsed_result
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        client::test::{client, CHAIN_ID, VALIDATOR_CONTROL_ADDRESS},
        signer::basic_signer::test::TRUSTEE_ACC,
        utils::init_env_logger,
    };
    use once_cell::sync::Lazy;

    pub static VALIDATOR_ADDRESS: Lazy<Address> =
        Lazy::new(|| Address::new("0x93917cadbace5dfce132b991732c6cda9bcc5b8a"));

    mod build_add_validator_transaction {
        use super::*;

        #[test]
        fn build_add_validator_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction = ValidatorControl::build_add_validator_transaction(
                &client,
                &TRUSTEE_ACC,
                &VALIDATOR_ADDRESS,
            )
            .unwrap();
            let expected_data = [
                77, 35, 140, 142, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147, 145, 124, 173, 186, 206,
                93, 252, 225, 50, 185, 145, 115, 44, 108, 218, 155, 204, 91, 138,
            ];

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
                to: VALIDATOR_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data.into(),
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_remove_validator_transaction {
        use super::*;

        #[test]
        fn build_remove_validator_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction = ValidatorControl::build_remove_validator_transaction(
                &client,
                &TRUSTEE_ACC,
                &VALIDATOR_ADDRESS,
            )
            .unwrap();
            let expected_data = [
                64, 161, 65, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147, 145, 124, 173, 186, 206,
                93, 252, 225, 50, 185, 145, 115, 44, 108, 218, 155, 204, 91, 138,
            ];

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(TRUSTEE_ACC.clone()),
                to: VALIDATOR_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: expected_data.into(),
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod build_get_validators_transaction {
        use super::*;

        #[test]
        fn build_get_validators_transaction_test() {
            init_env_logger();
            let client = client(None);
            let transaction = ValidatorControl::build_get_validators_transaction(&client).unwrap();
            let encoded_method = [183, 171, 77, 181];

            let expected_transaction = Transaction {
                type_: TransactionType::Read,
                from: None,
                to: VALIDATOR_CONTROL_ADDRESS.to_string(),
                chain_id: CHAIN_ID,
                data: encoded_method.into(),
                signed: None,
            };

            assert_eq!(expected_transaction, transaction);
        }
    }

    mod parse_get_validators_result {
        use std::vec;

        use super::*;

        #[test]
        fn parse_get_validators_result_test() {
            let client = client(None);
            let validator_list_bytes = [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147, 145, 124, 173,
                186, 206, 93, 252, 225, 50, 185, 145, 115, 44, 108, 218, 155, 204, 91, 138, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 169, 124, 154, 175, 4, 241, 143, 48, 20, 195, 46,
                3, 109, 208, 172, 118, 218, 95, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 206, 65,
                47, 152, 131, 119, 227, 31, 77, 15, 241, 45, 116, 223, 115, 181, 28, 66, 208, 202,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 152, 193, 51, 68, 150, 97, 74, 237, 73, 210,
                232, 21, 38, 208, 137, 247, 38, 79, 237, 156,
            ];
            let expected_validator_list = vec![
                Address::new("0x93917cadbace5dfce132b991732c6cda9bcc5b8a"),
                Address::new("0x27a97c9aaf04f18f3014c32e036dd0ac76da5f18"),
                Address::new("0xce412f988377e31f4d0ff12d74df73b51c42d0ca"),
                Address::new("0x98c1334496614aed49d2e81526d089f7264fed9c"),
            ]; // initial localnet validator list

            let parse_get_validators_result =
                ValidatorControl::parse_get_validators_result(&client, &validator_list_bytes)
                    .unwrap();

            assert_eq!(expected_validator_list, parse_get_validators_result);
        }
    }
}
