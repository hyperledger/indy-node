# Hands on Walkthrough

This walkthrough goes through some of the detailed steps mentioned in [Setting up a New Network](../../docs/source/NewNetwork/NewNetwork.md)

For the sake of simplicity this walkthrough runs all of the nodes on the local machine.  As a result it uses the local python install version of some of the commands rather than the production level Debian package install version of the commands documented in the [Setting up a New Network](../../docs/source/NewNetwork/NewNetwork.md) guide.

1. Open indy-cli by executing `indy-cli`
   
   Note that the command prompt changed to `indy>`.

2. Create and open a wallet in the indy-cli.

   `indy>wallet create newNetwork key=key`

   If not already opened, open the wallet
   `indy> wallet open newNetwork key=key`

3. Create DIDs for Trustees.

   ```
   newNetwork:indy> did new seed=000000000000000000000000Trustee1
   Did "V4SGRU86Z58d6TV7PBUe6f" has been created with "~CoRER63DVYnWZtK8uAzNbx" verkey
   newNetwork:indy> did new seed=000000000000000000000000Trustee2
   Did "LnXR1rPnncTPZvRdmJKhJQ" has been created with "~RTBtVN3iwcFhbWZzohFTMi" verkey
   newNetwork:indy> did new seed=000000000000000000000000Trustee3
   Did "PNQm3CwyXbN5e39Rw3dXYx" has been created with "~AHtGeRXtGjVfXALtXP9WiX" verkey
   ```

   > Warning: The used seed if used twice will result in the same DID and keys! 

4. Create DIDs for Stewards

   For the sake of this tutorial all DIDs and Stewards are running on the same machine. Normally this would be independent machines and organizations.

   ```
   newNetwork:indy> did new seed=000000000000000000000000Steward1
   Did "Th7MpTaRZVRYnPiabds81Y" has been created with "~7TYfekw4GUagBnBVCqPjiC" verkey
   newNetwork:indy> did new seed=000000000000000000000000Steward2
   Did "EbP4aYNeTHL6q385GuVpRV" has been created with "~RHGNtfvkgPEUQzQNtNxLNu" verkey
   newNetwork:indy> did new seed=000000000000000000000000Steward3
   Did "4cU41vWW82ArfxJxHkzXPG" has been created with "~EMoPA6HrpiExVihsVfxD3H" verkey
   newNetwork:indy> did new seed=000000000000000000000000Steward4
   Did "TWwCRQRZ2ZHMJFn9TzLp7W" has been created with "~UhP7K35SAXbix1kCQV4Upx" verkey
   ```
5. Edit `/etc/indy/indy_config.py` and change the network name.
   `NETWORK_NAME = "newNetwork"`

6. `mkdir /var/lib/indy/newNetwork`

7. Create Validator Node keys

   > The seed will be randomly generated. As mentioned above with the seed you can recreate the key!

   ```
   $ init_indy_node Steward1 0.0.0.0 9701 0.0.0.0 9702
   Node-stack name is Steward1
   Client-stack name is Steward1C
   Generating keys for random seed b'88c26d3C92bc33Be077Bf22FCBa60E2A'
   Init local keys for client-stack
   Public key is DGM7x7SQvjKjfUa7VLo5gGCZ6WfKASo6Cp5uP3aBRf7j
   Verification key is DJrzRm3ahRkz2pesFVtmH8wA3S3z63XayZgDvV21b4BF
   Init local keys for node-stack
   Public key is DGM7x7SQvjKjfUa7VLo5gGCZ6WfKASo6Cp5uP3aBRf7j
   Verification key is DJrzRm3ahRkz2pesFVtmH8wA3S3z63XayZgDvV21b4BF
   BLS Public key is 3k9aPxmqMYY4QQ3MK88Pot5QmqxfaaxuzMeGnKYT8j1Ds1Rcmq2zmjQmLMtKvBzC89E7yCQyiQ9HEDcGAZi6zmarMCQNkY9oYCAUVJGrZgxBE4a1oj7VYKw7zuGpMwsKLPGLcTGwpmX9LS6f5ykbazEwEgQRTiWj2epRKxZC87DLwbH
   Proof of possession for BLS key is RT5vLkN7639sXwYMBWkuFnzSM7ezEb49ZZExf6htH1WBWyuYgJsRTqT71HWaizfFLi1zp63eNGKKVzzyMaETYoj8QoV3GejHeZzP7LydJQpHQ5VPuLW3NUy5BGH4Xt7RkCT5pUbwhjz6mwxXfGAtQot7kiMH18QrpcazAmHrFPXKe7

   $ init_indy_node Steward2 0.0.0.0 9703 0.0.0.0 9704
   Node-stack name is Steward2
   Client-stack name is Steward2C
   Generating keys for random seed b'Fa4F5cd101f891ca0Cfa4E02C9Bf1769'
   Init local keys for client-stack
   Public key is FF3Aq98cJ2QT5EDmtshfVkgyjm9dxJV7xbtFrtMQbKeD
   Verification key is EQJ92vJVaAihejc9N2Yqy59L7ixVKMx2FgaXxD8F6vs7
   Init local keys for node-stack
   Public key is FF3Aq98cJ2QT5EDmtshfVkgyjm9dxJV7xbtFrtMQbKeD
   Verification key is EQJ92vJVaAihejc9N2Yqy59L7ixVKMx2FgaXxD8F6vs7
   BLS Public key is XvFCAC84AjEzcLFfdNQq17rGxheUbd95MCTkg8Bw3CNRR61isy5uNiqaoxZgNZac2MEvZoXX7Wk27YUMB9mc4XFdAHRJiVVs3UcB3giBuhbv4om6GjouGcKWYsFkffA4tvWPyeDDn5ifxZaJBDHVR4AHcvUNxFipGnEptFSDzayzBG
   Proof of possession for BLS key is RXfySA7HWDh57hm3GRKqj1DcMPq66fLJHMzaN76U1XqdUaRTRmBtxgSREtEvudSNFL8woXJzqS7VnJehZNd8hXf4bipdBhJ4J7hzBwhpbXfsuH2yH6XExBrxyPCwyQ9K9RAQraHz2RTLhs8r93HNzjauUARbw5ADv2F42FW69kWbdR

   $ init_indy_node Steward3 0.0.0.0 9705 0.0.0.0 9706
   Node-stack name is Steward3
   Client-stack name is Steward3C
   Generating keys for random seed b'A59c0EFB9cD7Eccdd4483a3BFbd36EB5'
   Init local keys for client-stack
   Public key is H3oLLToN9Wy1Yb9R9EMZXot8xCTnQLWMiSHRCpQm9fRD
   Verification key is EktpqGnexWaiQyr9vcXDTgNYwqT8cxmAfnX8N7qWwEcC
   Init local keys for node-stack
   Public key is H3oLLToN9Wy1Yb9R9EMZXot8xCTnQLWMiSHRCpQm9fRD
   Verification key is EktpqGnexWaiQyr9vcXDTgNYwqT8cxmAfnX8N7qWwEcC
   BLS Public key is 13U7tXXXRTLeavMEQk7MqECuKkuFrHPAwidf2cVqhaJoABmHc4SBMXHVJJkc1pJNvjLu894UZ6pSt3aAYZ5nQrfkuqbBUEToWb5vZSLHTTNnznkzx5PStPFSZkYUuA4bYNLk5b8GbwrHFKjrjqzCdjEWs2hDipAmXfd9NBh3BTEwAxS
   Proof of possession for BLS key is RHeKLLefbDdgBMpZ9AUrS8EHPDRnFXNiJ1z8LUgqPa8eUGyeRkAR2ppPkYqcLc9ekzG8cYZMTGx8y52sZ1q2QWqs3BYBH2i3H2WxL4icRq9Kj4kqs3BQadtPWBSq4vEaWTwwieuUXFYqpvk1ALCSNmS9NmMYXYyTL8uzrstviomjXm

   $ init_indy_node Steward4 0.0.0.0 9707 0.0.0.0 9708
   Node-stack name is Steward4
   Client-stack name is Steward4C
   Generating keys for random seed b'F20fc06eab86A896A6Ae5D8AfEA46B68'
   Init local keys for client-stack
   Public key is GJVyfv4XXGHYDYmiifu8XmXyTx9jGb39hACRU23rT9Ww
   Verification key is 8XFTwX3rHVUBddyruNTzKnBdbFqWz8eZPRasyySLD7Sv
   Init local keys for node-stack
   Public key is GJVyfv4XXGHYDYmiifu8XmXyTx9jGb39hACRU23rT9Ww
   Verification key is 8XFTwX3rHVUBddyruNTzKnBdbFqWz8eZPRasyySLD7Sv
   BLS Public key is oy7vASnhYAYo9fV1MzFSeCHEmyd2dQze6dmwWd5unwoySsA2UauUaKpV6QqwL9WQzQYRXZAoDT9jXGWwGFgCKWKVinFPj2TU5qsqAFt6PcXxQ7ZpBMEiUhQreqQv9BQsb7Upx9cNZKm4wKRyjCryX3TELb3xzz51wwsdeY8hduAKvb
   Proof of possession for BLS key is QsrUH1e5zsdiEGij1NeY9S7CwzUdU2rzjskHNGHCQ8rtgYZyBC99MgRPzgkJHP86nWQUo2fSRvyWLQdBwvWfNtSqUBQgVScQPHg9CJXWWohWnzSP4ViBo8EEeGXEoP2NPeRnFCCfuhYAC7stZgBATFyvdFRwG58ws76qQQQsfDDHBV
   ```

8. Fill in the spreadsheet.
   
9. Download the script from [https://github.com/sovrin-foundation/steward-tools/tree/master/create_genesis] and generate the genesis file.

   ```
   $ python genesis_from_files.py --trustees Trustees.csv --stewards Stewards.csv 
   DEBUG:root:new line check for file: ./pool_transactions_genesis
   INFO:root:Starting ledger...
   INFO:root:Recovering tree from transaction log
   INFO:root:Recovered tree in 0.002561586000410898 seconds
   DEBUG:root:new line check for file: ./domain_transactions_genesis
   INFO:root:Starting ledger...
   INFO:root:Recovering tree from transaction log
   INFO:root:Recovered tree in 0.000322740000228805 seconds
   ```
10. `cp domain_transactions_genesis /var/lib/indy/newNetwork/ && cp pool_transactions_genesis /var/lib/indy/newNetwork/`

11. Start the nodes:

    ```
    start_indy_node Steward1 0.0.0.0 9701 0.0.0.0 9702
    start_indy_node Steward2 0.0.0.0 9703 0.0.0.0 9704
    start_indy_node Steward3 0.0.0.0 9705 0.0.0.0 9706
    start_indy_node Steward4 0.0.0.0 9707 0.0.0.0 9708     
    ```
