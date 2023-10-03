use crate::{
    client::{client::Client, Transaction},
    error::VdrResult,
    signer::Signer,
};
use web3::{
    helpers,
    transports::Http,
    types::{Bytes, CallRequest},
    Web3,
};

pub struct Web3Client {
    pub client: Web3<Http>,
}

impl Web3Client {
    pub fn new(node_address: &str) -> VdrResult<Web3Client> {
        let transport = Http::new(node_address)?;
        let web3 = Web3::new(transport);
        Ok(Web3Client { client: web3 })
    }
}

#[async_trait::async_trait]
impl Client for Web3Client {
    async fn sign_transaction(
        &self,
        transaction: &Transaction,
        signer: &Signer,
    ) -> VdrResult<Vec<u8>> {
        let signed_transaction = self
            .client
            .accounts()
            .sign_transaction(transaction.clone().into(), signer)
            .await?
            .raw_transaction
            .0;
        Ok(signed_transaction)
    }

    async fn submit_transaction(&self, transaction: &Vec<u8>) -> VdrResult<Vec<u8>> {
        let response = self
            .client
            .eth()
            .send_raw_transaction(transaction.clone().into())
            .await?;
        Ok(response.0.to_vec())
    }

    async fn call_transaction(&self, transaction: &Transaction) -> VdrResult<Vec<u8>> {
        let request = CallRequest::builder()
            .to(transaction.to)
            .data(Bytes(transaction.data.clone()))
            .build();
        let response = self.client.eth().call(request, None).await?;
        Ok(response.0)
    }
}
