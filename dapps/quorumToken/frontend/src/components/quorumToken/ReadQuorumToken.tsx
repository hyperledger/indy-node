import React, {useEffect, useState } from 'react';
import {Text} from '@chakra-ui/react'
import {QuorumTokenABI as abi} from './QuorumTokenABI'
import {ethers, Contract} from 'ethers'

declare let window: any;

interface ReadQuorumTokenProps {
    addressContract: string,
    currentAccount: string | undefined
}

export default function ReadQuorumToken(props:ReadQuorumTokenProps){
  const addressContract = props.addressContract
  const currentAccount = props.currentAccount
  const [totalSupply,setTotalSupply]=useState<string>()
  const [symbol,setSymbol]= useState<string>("")
  const [balance, setBalance] =useState<number|undefined>(undefined)

  useEffect( () => {
    if(!window.ethereum) return;
    const provider = new ethers.BrowserProvider(window.ethereum);
    const erc20:Contract  = new ethers.Contract(addressContract, abi, provider);

    provider.getCode(addressContract).then((result:string)=>{
      //check whether it is a contract
      if(result === '0x') return

      erc20.symbol().then((result:string)=>{
          setSymbol(result)
      }).catch('error', console.error)
      erc20.totalSupply().then((result:string)=>{
          setTotalSupply(ethers.formatEther(result))
      }).catch('error', console.error);

    })
  },[])  

  // when currentAccount changes, we call this hook ie useEffect(()=>{ .... },[currentAccount]
  // 
  useEffect(()=>{
    if(!window.ethereum) return
    if(!currentAccount) return

    queryTokenBalance(window);
    const provider = new ethers.BrowserProvider(window.ethereum);
    const erc20:Contract = new ethers.Contract(addressContract, abi, provider);

    // listen for changes on an Ethereum address
    console.log(`listening for Transfer...`)
    const fromMe = erc20.filters.Transfer(currentAccount, null)
    erc20.on(fromMe, (from, to, amount, event) => {
        console.log('Transfer|sent',  {from, to, amount, event} )
        queryTokenBalance(window)
    })

    const toMe = erc20.filters.Transfer(null, currentAccount)
    erc20.on(toMe, (from, to, amount, event) => {
        console.log('Transfer|received',  {from, to, amount, event} )
        queryTokenBalance(window)
    })

    // remove listener when the component is unmounted
    return () => {
        erc20.removeAllListeners(toMe)
        erc20.removeAllListeners(fromMe)
    }    
  }, [currentAccount])


  async function queryTokenBalance(window:any){
    const provider = new ethers.BrowserProvider(window.ethereum);
    const erc20:Contract = new ethers.Contract(addressContract, abi, provider);

    erc20.balanceOf(currentAccount)
    .then((result:string)=>{
        setBalance(Number(ethers.formatEther(result)))
    }).catch((e:Error)=>console.log(e))
  }

  return (
    <div>
        <Text><b>ERC20 Contract Address</b>:  {addressContract}</Text>
        <Text><b>QuorumToken totalSupply</b>: {totalSupply} {symbol}</Text>
        <Text><b>QuorumToken in current account</b>: {balance} {symbol}</Text>
    </div>
  )
}
