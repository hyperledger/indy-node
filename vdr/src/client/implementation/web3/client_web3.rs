use crate::{
    client::{client::Client, types::Transaction},
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
    pub fn new(node_address: &str) -> Web3Client {
        let transport = Http::new(node_address).unwrap();
        let web3 = Web3::new(transport);
        return Web3Client { client: web3 };
    }
}

#[async_trait::async_trait]
impl Client for Web3Client {
    async fn sign_transaction(&self, transaction: Transaction, signer: &Signer) -> Vec<u8> {
        self.client
            .accounts()
            .sign_transaction(transaction.into(), signer)
            .await
            .unwrap()
            .raw_transaction
            .0
    }

    async fn send_raw_transaction(&self, transaction: &[u8]) -> String {
        let result = self
            .client
            .eth()
            .send_raw_transaction(transaction.into())
            .await
            .unwrap();
        let hash = helpers::serialize(&result);
        hash.as_str().unwrap().to_string()
    }

    async fn call(&self, transaction: &Transaction) -> Vec<u8> {
        let request = CallRequest::builder()
            .to(transaction.to)
            .data(Bytes(transaction.data.clone()))
            .build();
        self.client.eth().call(request, None).await.unwrap().0
    }
}
