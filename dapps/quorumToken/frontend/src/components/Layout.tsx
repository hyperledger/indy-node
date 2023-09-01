import React, { ReactNode } from 'react'
import { Container, Flex, useColorModeValue, Spacer, Heading, Center, Text } from '@chakra-ui/react'

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div>

      <Flex w="100%" bg={useColorModeValue('gray.100', 'gray.900')} px="6" py="5" align="center" justify="space-between">
        <Heading size="md">Quorum Quickstart DApp</Heading>
        <Spacer />
      </Flex>

      <Container maxW="container.lg" py='8'>
        {children}
      </Container>

      <Center as="footer" bg={useColorModeValue('gray.100', 'gray.700')} p={6}>
        <Text fontSize="md"> &copy; {new Date().getFullYear()} ConsenSys Software, Inc. All rights reserved.</Text>
      </Center>

    </div>
  )
}