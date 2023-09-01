import React, { useEffect, useState } from 'react';
import { Text, Button, Input , NumberInput,  NumberInputField,  FormControl,  FormLabel } from '@chakra-ui/react';
import {ethers, Contract} from 'ethers';
import {QuorumTokenABI as abi} from './QuorumTokenABI';
import { TransactionResponse,TransactionReceipt } from "@ethersproject/abstract-provider";

declare let window: any;

interface Props {
    addressContract: string,
    currentAccount: string | undefined
}

export default function TransferQuorumToken(props:Props){
  const addressContract = props.addressContract
  const currentAccount = props.currentAccount
  const [amount, setAmount]=useState<string>('100')
  const [toAddress, setToAddress]=useState<string>("")

  const handleChange = (value:string) => setAmount(value)

  // https://docs.ethers.org/v6/getting-started/#starting-contracts
  async function transfer(event:React.FormEvent) {
    event.preventDefault()
    // const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const erc20:Contract = new ethers.Contract(addressContract, abi, signer);
    
    erc20.transfer(toAddress, ethers.parseEther(amount))
      .then((tr: TransactionResponse) => {
        console.log(`TransactionResponse TX hash: ${tr.hash}`)
        // todo: maybe put this in a modal thing?
        tr.wait().then((receipt:TransactionReceipt)=>{console.log("transfer receipt",receipt)})
      })
      .catch((e:Error)=>console.log(e))

 }


  return (
    <form onSubmit={transfer}>
    <FormControl>
    <FormLabel htmlFor='amount'>Amount: </FormLabel>
      <NumberInput defaultValue={amount} min={10} max={1000} onChange={handleChange}>
        <NumberInputField />
      </NumberInput>
      <FormLabel htmlFor='toaddress'>To address: </FormLabel>
      <Input id="toaddress" type="text" required  onChange={(e) => setToAddress(e.target.value)} my={3}/>
      <Button type="submit" isDisabled={!currentAccount}>Transfer</Button>
    </FormControl>
    </form>
  )
}
