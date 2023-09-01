
import React, {useEffect, useState } from 'react';
import { Heading, Text, VStack, Box, Button, Input, Spacer, Flex } from '@chakra-ui/react'

interface MMAccountProps {
  balance: string | undefined,
  chainId: number | undefined
  erc20ContractAddress: string
  deployedAddressHandler: any
}

export default function MMAccount(props:MMAccountProps){

  return (
    <Box  mb={0} p={4} w='100%' borderWidth="1px" borderRadius="lg">
      <Heading my={4}  fontSize='xl'>Account</Heading>
      <Text my={4}>Details of the account connected to Metamask</Text>
      <Text><b>Balance of current account (ETH)</b>: {props.balance}</Text>
      <Text><b>ChainId</b>: {props.chainId} </Text>
      {/* todo: fix formatting here */}
      <Text><b>Address that the QuorumToken was deployed to</b>: </Text>
      <Input value={props.erc20ContractAddress}  name="erc20ContractAddress" onChange={props.deployedAddressHandler} />
    </Box>
  )
}