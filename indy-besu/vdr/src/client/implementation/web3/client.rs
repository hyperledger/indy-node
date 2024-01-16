use crate::{
    client::{constants::GAS, implementation::web3::signer::Web3Signer, Client, Transaction},
    error::{VdrError, VdrResult},
    signer::Signer,
};

use crate::client::{PingStatus, TransactionType};
use log::{trace, warn};
use serde_json::json;
use std::{str::FromStr, time::Duration};
use web3::{
    api::Eth,
    transports::Http,
    types::{Address, Bytes, CallRequest, TransactionParameters, H256, U256},
    Web3,
};

pub struct Web3Client {
    client: Web3<Http>,
    signer: Option<Box<dyn Signer>>,
}

const POLL_INTERVAL: u64 = 200;
const NUMBER_TX_CONFIRMATIONS: usize = 1; // FIXME: what number of confirmation events should we wait? 2n+1?

impl Web3Client {
    pub fn new(node_address: &str, signer: Option<Box<dyn Signer>>) -> VdrResult<Web3Client> {
        trace!(
            "Started creating new Web3Client. Node address: {}",
            node_address
        );

        let transport = Http::new(node_address).map_err(|_| VdrError::ClientNodeUnreachable)?;
        let web3 = Web3::new(transport);
        let web3_client = Web3Client {
            client: web3,
            signer,
        };

        trace!("Created new Web3Client. Node address: {}", node_address);

        Ok(web3_client)
    }

    pub fn eth(&self) -> Eth<Http> {
        self.client.eth()
    }
}

#[async_trait::async_trait]
impl Client for Web3Client {
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Transaction> {
        trace!(
            "Sign transaction process has started. Transaction: {:?}",
            transaction
        );

        let signer = self
            .signer
            .as_ref()
            .ok_or_else(|| {
                let vdr_error = VdrError::ClientInvalidState("Signer is not set".to_string());

                warn!(
                    "Error: {} during signing transaction: {:?}",
                    vdr_error, transaction
                );

                vdr_error
            })?
            .as_ref();
        let account = transaction.from.clone().ok_or_else(|| {
            let vdr_error =
                VdrError::ClientInvalidTransaction("Missing sender address".to_string());

            warn!(
                "Error: {} during signing transaction: {:?}",
                vdr_error, transaction
            );

            vdr_error
        })?;

        let signer = Web3Signer::new(account, signer);

        let to = Address::from_str(&transaction.to).map_err(|_| {
            let vdr_error = VdrError::ClientInvalidTransaction(format!(
                "Invalid transaction target address {}",
                transaction.to
            ));

            warn!(
                "Error: {} during signing transaction: {:?}",
                vdr_error, transaction
            );

            vdr_error
        })?;
        let web3_transaction = TransactionParameters {
            to: Some(to),
            data: Bytes::from(transaction.clone().data),
            chain_id: Some(transaction.chain_id),
            gas: U256([GAS, 0, 0, 0]),
            gas_price: Some(U256([0, 0, 0, 0])),
            ..Default::default()
        };

        let signed_transaction = self
            .client
            .accounts()
            .sign_transaction(web3_transaction, signer)
            .await?
            .raw_transaction
            .0;

        trace!("Signed transaction: {:?}", transaction);

        Ok(Transaction {
            signed: Some(signed_transaction),
            ..transaction.clone()
        })
    }

    async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        trace!(
            "Submit transaction process has started. Transaction: {:?}",
            transaction
        );

        if transaction.type_ != TransactionType::Write {
            let vdr_error =
                VdrError::ClientInvalidTransaction("Write transaction expected".to_string());

            warn!(
                "Error: {} during submitting transaction: {:?}",
                vdr_error, transaction
            );

            return Err(vdr_error);
        }
        let signed_transaction = transaction.signed.as_ref().ok_or_else(|| {
            let vdr_error = VdrError::ClientInvalidTransaction("Missing signature".to_string());

            warn!(
                "Error: {} during submitting transaction: {:?}",
                vdr_error, transaction
            );

            vdr_error
        })?;

        let receipt = self
            .client
            .send_raw_transaction_with_confirmation(
                Bytes::from(signed_transaction.clone()),
                Duration::from_millis(POLL_INTERVAL),
                NUMBER_TX_CONFIRMATIONS,
            )
            .await?;

        trace!("Submitted transaction: {:?}", transaction);

        Ok(receipt.transaction_hash.0.to_vec())
    }

    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        trace!(
            "Call transaction process has started. Transaction: {:?}",
            transaction
        );

        if transaction.type_ != TransactionType::Read {
            let vdr_error =
                VdrError::ClientInvalidTransaction("Read transaction expected".to_string());

            warn!(
                "Error: {} during calling transaction: {:?}",
                vdr_error, transaction
            );

            return Err(vdr_error);
        }
        let address = Address::from_str(&transaction.to).map_err(|_| {
            let vdr_error = VdrError::ClientInvalidTransaction(format!(
                "Invalid transaction target address {}",
                transaction.to
            ));

            warn!(
                "Error: {} during calling transaction: {:?}",
                vdr_error, transaction
            );

            vdr_error
        })?;
        let request = CallRequest::builder()
            .to(address)
            .data(Bytes(transaction.data.clone()))
            .build();
        let response = self.client.eth().call(request, None).await?;

        trace!("Called transaction: {:?}", transaction);

        Ok(response.0.to_vec())
    }

    async fn get_receipt(&self, hash: &[u8]) -> VdrResult<String> {
        let receipt = self
            .client
            .eth()
            .transaction_receipt(H256::from_slice(hash))
            .await?
            .ok_or_else(|| {
                let vdr_error =
                    VdrError::ClientInvalidResponse("Missing transaction receipt".to_string());

                warn!("Error: {} getting receipt", vdr_error,);

                vdr_error
            })
            .map(|receipt| json!(receipt).to_string());

        trace!("Got receipt: {:?}", receipt);

        receipt
    }

    async fn ping(&self) -> VdrResult<PingStatus> {
        let ping_result = match self.client.eth().block_number().await {
            Ok(_current_block) => Ok(PingStatus::ok()),
            Err(_) => Ok(PingStatus::err("Could not get current network block")),
        };

        trace!("Ping result: {:?}", ping_result);

        ping_result
    }
}
