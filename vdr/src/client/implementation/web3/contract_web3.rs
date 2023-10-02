use crate::client::{
    client::Contract, implementation::web3::client_web3::Web3Client, ContractSpec,
};
use std::str::FromStr;
use web3::{
    contract::Contract as Web3ContractImpl,
    ethabi::{Address, Function, Token},
    transports::Http,
};

pub struct Web3Contract {
    contract: Web3ContractImpl<Http>,
}

impl Web3Contract {
    pub fn new(web3_client: &Web3Client, contract_spec: &ContractSpec) -> Web3Contract {
        let abi = std::fs::read(&contract_spec.abi_path).unwrap();
        let contract = Web3ContractImpl::from_json(
            web3_client.client.eth(),
            Address::from_str(&contract_spec.address).unwrap(),
            abi.as_slice(),
        )
        .unwrap();
        Web3Contract { contract }
    }

    fn function(&self, name: &str) -> &Function {
        &self.contract.abi().function(name).unwrap()
    }
}

impl Contract for Web3Contract {
    fn address(&self) -> Address {
        self.contract.address()
    }

    fn encode_input(&self, method: &str, params: &[Token]) -> Vec<u8> {
        self.function(method).encode_input(params).unwrap()
    }

    fn decode_output(&self, method: &str, output: &[u8]) -> Vec<Token> {
        self.function(method).decode_output(output).unwrap()
    }
}
