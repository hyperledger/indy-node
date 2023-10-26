use crate::{
    client::{ContractParam, Transaction, TransactionBuilder, TransactionParser, TransactionType},
    error::VdrResult,
    LedgerClient,
};

use super::validator_info::ValidatorAddresses;

pub struct ValidatorControl;

impl ValidatorControl {
    const CONTRACT_NAME: &'static str = "ValidatorControl";
    const METHOD_ADD_VALIDATOR: &'static str = "addValidator";
    const METHOD_REMOVE_VALIDATOR: &'static str = "removeValidator";
    const METHOD_GET_VALIDATORS: &'static str = "getValidators";

    pub fn build_add_validator_transaction(
        client: &LedgerClient,
        from: &str,
        validator_address: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_ADD_VALIDATOR)
            .add_param(ContractParam::Address(validator_address.parse().unwrap()))
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(&client)
    }

    pub fn build_remove_validator_transaction(
        client: &LedgerClient,
        from: &str,
        validator_address: &str,
    ) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_REMOVE_VALIDATOR)
            .add_param(ContractParam::Address(validator_address.parse().unwrap()))
            .set_type(TransactionType::Write)
            .set_from(from)
            .build(&client)
    }

    pub fn build_get_validators_transaction(client: &LedgerClient) -> VdrResult<Transaction> {
        TransactionBuilder::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_VALIDATORS)
            .set_type(TransactionType::Read)
            .build(&client)
    }

    pub fn parse_get_validators_result(
        client: &LedgerClient,
        bytes: &[u8],
    ) -> VdrResult<ValidatorAddresses> {
        TransactionParser::new()
            .set_contract(Self::CONTRACT_NAME)
            .set_method(Self::METHOD_GET_VALIDATORS)
            .parse::<ValidatorAddresses>(&client, bytes)
    }

    pub async fn add_validator(
        client: &LedgerClient,
        from: &str,
        validator_address: &str,
    ) -> VdrResult<String> {
        let transaction = Self::build_add_validator_transaction(client, from, validator_address)?;
        client.sign_and_submit(&transaction).await
    }

    pub async fn remove_validator(
        client: &LedgerClient,
        from: &str,
        validator_address: &str,
    ) -> VdrResult<String> {
        let transaction =
            Self::build_remove_validator_transaction(client, from, validator_address)?;
        client.sign_and_submit(&transaction).await
    }

    pub async fn get_validators(client: &LedgerClient) -> VdrResult<Vec<String>> {
        let transaction = Self::build_get_validators_transaction(client)?;
        let result = client.submit_transaction(&transaction).await?;
        Self::parse_get_validators_result(client, &result)
    }
}

#[cfg(test)]
pub mod test {
    use super::*;
    use crate::{
        client::test::{client, CHAIN_ID, VALIDATOR_CONTROL_ADDRESS},
        signer::signer::test::ACCOUNT,
    };

    pub const VALIDATOR_ADDRESS: &'static str = "0x93917cadbace5dfce132b991732c6cda9bcc5b8a";

    mod build_add_validator_transaction {
        use super::*;

        #[test]
        fn build_add_validator_transaction_test() {
            let client = client();
            let transaction = ValidatorControl::build_add_validator_transaction(
                &client,
                ACCOUNT,
                VALIDATOR_ADDRESS,
            )
            .unwrap();
            let expected_data = [
                77, 35, 140, 142, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147, 145, 124, 173, 186, 206,
                93, 252, 225, 50, 185, 145, 115, 44, 108, 218, 155, 204, 91, 138,
            ];

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
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
            let client = client();
            let transaction = ValidatorControl::build_remove_validator_transaction(
                &client,
                ACCOUNT,
                VALIDATOR_ADDRESS,
            )
            .unwrap();
            let expected_data = [
                64, 161, 65, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 147, 145, 124, 173, 186, 206,
                93, 252, 225, 50, 185, 145, 115, 44, 108, 218, 155, 204, 91, 138,
            ];

            let expected_transaction = Transaction {
                type_: TransactionType::Write,
                from: Some(ACCOUNT.to_string()),
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
            let client = client();
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
}
