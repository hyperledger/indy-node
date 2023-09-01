
import type { AppProps } from "next/app";
import { ChakraProvider } from "@chakra-ui/react";
import "../../styles/globals.css";
import Layout from '../components/Layout';

function MyApp({ Component, pageProps, router }: AppProps) {

  return (
    <ChakraProvider>
      <title>Quorum Quickstart DApp</title>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </ChakraProvider>
  )
}

export default MyApp;
