use crate::{
    client::{client::Client, implementation::web3::signer::Web3Signer, Transaction},
    error::{VdrError, VdrResult},
    signer::Signer,
};
use serde_json::json;
use std::str::FromStr;
use web3::{
    api::Eth,
    transports::Http,
    types::{Address, Bytes, CallRequest, TransactionParameters, H256},
    Web3,
};

pub struct Web3Client {
    client: Web3<Http>,
    signer: Option<Web3Signer>,
}

impl Web3Client {
    pub fn new(
        node_address: &str,
        signer: Option<Box<dyn Signer + 'static + Send + Sync>>,
    ) -> VdrResult<Web3Client> {
        let transport = Http::new(node_address)?;
        let web3 = Web3::new(transport);
        let web3_signer = signer.map(|signer| Web3Signer::new(signer));
        Ok(Web3Client {
            client: web3,
            signer: web3_signer,
        })
    }

    pub fn eth(&self) -> Eth<Http> {
        self.client.eth()
    }
}

#[async_trait::async_trait]
impl Client for Web3Client {
    async fn sign_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        let signer = self.signer.as_ref().ok_or(VdrError::Unexpected)?;
        let address = Address::from_str(&transaction.to).map_err(|_| VdrError::Unexpected)?;
        let transaction = TransactionParameters {
            to: Some(address),
            data: Bytes::from(transaction.clone().data),
            chain_id: Some(transaction.chain_id),
            ..Default::default()
        };
        let signed_transaction = self
            .client
            .accounts()
            .sign_transaction(transaction, signer)
            .await?
            .raw_transaction
            .0;
        Ok(signed_transaction)
    }

    async fn submit_transaction(&self, transaction: &[u8]) -> VdrResult<Vec<u8>> {
        let response = self
            .client
            .eth()
            .send_raw_transaction(Bytes::from(transaction))
            .await?;
        Ok(response.0.to_vec())
    }

    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        let address = Address::from_str(&transaction.to).map_err(|_| VdrError::Unexpected)?;
        let request = CallRequest::builder()
            .to(address)
            .data(Bytes(transaction.data.clone()))
            .build();
        let response = self.client.eth().call(request, None).await?;
        Ok(response.0)
    }

    async fn get_transaction_receipt(&self, hash: &[u8]) -> VdrResult<String> {
        self.client
            .eth()
            .transaction_receipt(H256::from_slice(hash))
            .await?
            .ok_or(VdrError::Unexpected)
            .map(|receipt| json!(receipt).to_string())
    }
}
