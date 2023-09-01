import type { NextPage } from 'next'
import { Heading, Text, VStack, Box, Button, Input, Spacer, Flex } from '@chakra-ui/react'
import { useState, useEffect} from 'react'
import {ethers} from "ethers"
import ReadQuorumToken from "../components/quorumToken/ReadQuorumToken"
import TransferQuorumToken from "../components/quorumToken/TransferQuorumToken"
import MMAccount from "../components/MMAccount"

declare let window:any

export default function Home() {

  const [balance, setBalance] = useState<string | undefined>();
  const [currentAccount, setCurrentAccount] = useState<string | undefined>();
  const [erc20ContractAddress, setErc20ContractAddress] = useState<string>("0x");
  const [chainId, setChainId] = useState<number | undefined>();

  useEffect( () => {
    if(!currentAccount || !ethers.isAddress(currentAccount)) return;
    if(!window.ethereum) return;
    const provider = new ethers.BrowserProvider(window.ethereum);
    provider.getBalance(currentAccount).then((result)=> {
      setBalance(ethers.formatEther(result));
    })
    provider.getNetwork().then((result)=>{
      setChainId(ethers.toNumber(result.chainId));
    })

  },[currentAccount])

  const onClickConnect = () => {
    if(!window.ethereum) {
      console.log("please install MetaMask");
      return;
    }

    const provider = new ethers.BrowserProvider(window.ethereum);
    // MetaMask requires requesting permission to connect users accounts
    provider.send("eth_requestAccounts", [])
    .then((accounts)=>{
      if(accounts.length>0) setCurrentAccount(accounts[0])
    })
    .catch((e)=>console.log(e))
  }

  const onClickDisconnect = () => {
    setBalance(undefined)
    setCurrentAccount(undefined)
  }

  const deployedAddressHandler = (e: any) => {
     setErc20ContractAddress(e.target.value);
  }

  return (
    <>
      <Heading as="h3" my={4}>QuorumToken</Heading>          
      <VStack>
      <Box w='100%' my={4}>
        {currentAccount  
          ? <Button type="button" w='100%' onClick={onClickDisconnect}>
                Connected to Metamask with account: {currentAccount}
            </Button>
          : <Button type="button" w='100%' onClick={onClickConnect}>
                  Connect to MetaMask
              </Button>
        }
        </Box>
        {currentAccount  
          ?<MMAccount 
            balance={balance} 
            chainId={chainId}
            erc20ContractAddress={erc20ContractAddress}
            deployedAddressHandler={deployedAddressHandler} />
          :<></>
        }

        {(erc20ContractAddress!="0x")  
          ?<Box mb={0} p={4} w='100%' borderWidth="1px" borderRadius="lg">
          <Heading my={4} fontSize='xl'>Read QuorumToken</Heading>
          <Text my={4}>Query the smart contract info at address provided</Text>
          <Spacer />
          <ReadQuorumToken 
            addressContract={erc20ContractAddress}
            currentAccount={currentAccount}
          />
        </Box>
        :<></>
        }

        {(erc20ContractAddress!="0x")  
          ?<Box  mb={0} p={4} w='100%' borderWidth="1px" borderRadius="lg">
          <Heading my={4}  fontSize='xl'>Transfer QuorumToken</Heading>
          <Text my={4}>Interact with the token</Text>
          <TransferQuorumToken
            addressContract={erc20ContractAddress}
            currentAccount={currentAccount}
          />
        </Box>
        :<></>
        } 

      </VStack>
    </>
  )
}
