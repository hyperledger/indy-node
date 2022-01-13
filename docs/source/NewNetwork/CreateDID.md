# Creating a DID using the `indy-cli`

You will need to perform the following commands once for each `indy-cli` machine that you want to run on. The following commands contain suggestions to save certain values in a secure place.  Please do not share those values or that place with anyone.

_If you just need to quickly generate a set of secrets (Seed and wallet key), or a Seed, DID, and Verkey and do not have an `indy-cli` environment already setup, you can use the `indy-cli` features integrated into `von-network`.  Refer to [Generate a set of Secrets](https://github.com/bcgov/von-network/blob/main/docs/Indy-CLI.md#generate-a-set-of-secrets), and [Generate your DID](https://github.com/bcgov/von-network/blob/main/docs/Indy-CLI.md#generate-your-did) for details._


1. Start your `indy-cli` using the instructions from [Installing the `indy-cli`](./CLIInstall.md) for your platform.

   All following commands are executing inside the `indy-cli`.

2. Create a wallet with:

   `wallet create <wallet_name> key`

   You will be prompted for a wallet key.  What you type will not be displayed on the console.  Your wallet key is a secure key that only you should know, and it should be randomly generated.  Save it in a secure place for later use.  You will use it every time you need to send transactions to the ledger from the `indy-cli`.
      
3. `wallet open wallet_name key`

   You will be prompted for your wallet key.  What you type will not be displayed on the console.

4. `did new seed`

   You will be prompted for a seed.  What you type will not be displayed on the console.

   If you have lost your original seed or have never created one, then create a new one. This seed is used to regenerate your DID and to add your DID to your wallet(s).  

   The seed is a 32 character string that only you can know. 
   
   > WARNING: Whoever knows your Seed can recreate your exact DID in their own wallet and use it to manage the ledger.
   
   Save your Seed in a secure place so that only you can recreate your DID whenever needed.  
   Also save the public DID and verkey generated from this step so that you will know and can verify your public DID.