use crate::{
    client::{constants::GAS, implementation::web3::signer::Web3Signer, Client, Transaction},
    error::{VdrError, VdrResult},
    signer::Signer,
};

use serde_json::json;
use std::str::FromStr;
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

impl Web3Client {
    pub fn new(
        node_address: &str,
        signer: Option<Box<dyn Signer + 'static + Send + Sync>>,
    ) -> VdrResult<Web3Client> {
        let transport = Http::new(node_address)?;
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
        let account = transaction.from.clone().ok_or(VdrError::Unexpected)?;
        let signer = self.signer.as_ref().ok_or(VdrError::Unexpected)?;
        if !signer.contain_key(&account) {
            return Err(VdrError::Unexpected);
        }
        let signer = Web3Signer::new(account, signer);
        let address = Address::from_str(&transaction.to).map_err(|_| VdrError::Unexpected)?;
        let web3_transaction = TransactionParameters {
            to: Some(address),
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
        let signed_transaction = Transaction {
            signed: Some(signed_transaction),
            ..transaction.clone()
        };
        Ok(signed_transaction)
    }

    async fn submit_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        let signed_transaction = transaction.signed.as_ref().ok_or(VdrError::Unexpected)?;
        let response = self
            .client
            .eth()
            .send_raw_transaction(Bytes::from(signed_transaction.clone()))
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
        Ok(response.0.to_vec())
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
