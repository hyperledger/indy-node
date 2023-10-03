use crate::{
    client::{client::Contract, implementation::web3::client_web3::Web3Client, ContractSpec},
    error::{VdrError, VdrResult},
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
    pub fn new(web3_client: &Web3Client, contract_spec: &ContractSpec) -> VdrResult<Web3Contract> {
        let abi = std::fs::read(&contract_spec.abi_path)?;
        let address = Address::from_str(&contract_spec.address)
            .map_err(|err| VdrError::Common(err.to_string()))?;
        let contract =
            Web3ContractImpl::from_json(web3_client.client.eth(), address, abi.as_slice())?;
        Ok(Web3Contract { contract })
    }

    fn function(&self, name: &str) -> VdrResult<&Function> {
        self.contract.abi().function(name).map_err(VdrError::from)
    }
}

impl Contract for Web3Contract {
    fn address(&self) -> Address {
        self.contract.address()
    }

    fn encode_input(&self, method: &str, params: &[Token]) -> VdrResult<Vec<u8>> {
        self.function(method)?
            .encode_input(params)
            .map_err(VdrError::from)
    }

    fn decode_output(&self, method: &str, output: &[u8]) -> VdrResult<Vec<Token>> {
        self.function(method)?
            .decode_output(output)
            .map_err(VdrError::from)
    }
}
