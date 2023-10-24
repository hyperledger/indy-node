use crate::{
    client::{constants::GAS, implementation::web3::signer::Web3Signer, Client, Transaction},
    error::{VdrError, VdrResult},
    signer::Signer,
};

use crate::client::{PingStatus, TransactionType};
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
    signer: Option<Box<dyn Signer + 'static + Send + Sync>>,
}

const POLL_INTERVAL: u64 = 200;
const NUMBER_TX_CONFIRMATIONS: usize = 1; // FIXME: what number of confirmation events should we wait? 2n+1?

impl Web3Client {
    pub fn new(
        node_address: &str,
        signer: Option<Box<dyn Signer + 'static + Send + Sync>>,
    ) -> VdrResult<Web3Client> {
        let transport = Http::new(node_address).map_err(|_| VdrError::ClientNodeUnreachable)?;
        let web3 = Web3::new(transport);
        Ok(Web3Client {
            client: web3,
            signer,
        })
    }

    pub fn eth(&self) -> Eth<Http> {
        self.client.eth()
    }
}

#[async_trait::async_trait]
impl Client for Web3Client {
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Transaction> {
        let signer = self.signer.as_ref().ok_or(VdrError::ClientInvalidState(
            "Signer is not set".to_string(),
        ))?;
        let account = transaction
            .from
            .clone()
            .ok_or(VdrError::ClientInvalidTransaction(
                "Missing sender address".to_string(),
            ))?;

        let signer = Web3Signer::new(account, signer);

        let to = Address::from_str(&transaction.to).map_err(|_| {
            VdrError::ClientInvalidTransaction(format!(
                "Invalid transaction target address {}",
                transaction.to
            ))
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

        Ok(Transaction {
            signed: Some(signed_transaction),
            ..transaction.clone()
        })
    }

    async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        if transaction.type_ != TransactionType::Write {
            return Err(VdrError::ClientInvalidTransaction(
                "Write transaction expected".to_string(),
            ));
        }
        let signed_transaction =
            transaction
                .signed
                .as_ref()
                .ok_or(VdrError::ClientInvalidTransaction(
                    "Missing signature".to_string(),
                ))?;

        let receipt = self
            .client
            .send_raw_transaction_with_confirmation(
                Bytes::from(signed_transaction.clone()),
                Duration::from_millis(POLL_INTERVAL),
                NUMBER_TX_CONFIRMATIONS,
            )
            .await?;
        Ok(receipt.transaction_hash.0.to_vec())
    }

    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        if transaction.type_ != TransactionType::Read {
            return Err(VdrError::ClientInvalidTransaction(
                "Read transaction expected".to_string(),
            ));
        }
        let address = Address::from_str(&transaction.to).map_err(|_| {
            VdrError::ClientInvalidTransaction(format!(
                "Invalid transaction target address {}",
                transaction.to
            ))
        })?;
        let request = CallRequest::builder()
            .to(address)
            .data(Bytes(transaction.data.clone()))
            .build();
        let response = self.client.eth().call(request, None).await?;
        Ok(response.0.to_vec())
    }

    async fn get_receipt(&self, hash: &[u8]) -> VdrResult<String> {
        self.client
            .eth()
            .transaction_receipt(H256::from_slice(hash))
            .await?
            .ok_or(VdrError::ClientInvalidResponse(
                "Missing transaction receipt".to_string(),
            ))
            .map(|receipt| json!(receipt).to_string())
    }

    async fn ping(&self) -> VdrResult<PingStatus> {
        match self.client.eth().block_number().await {
            Ok(_current_block) => Ok(PingStatus::ok()),
            Err(_) => Ok(PingStatus::err("Could not get current network block")),
        }
    }
}
