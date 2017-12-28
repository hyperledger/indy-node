# Helper Scripts

Indy-node comes with a number of useful helper scripts:
- `init_indy_keys`

    Initializes (or rotates) Node's keys (private and public ones) needed for communication with the Nodes via CurveCP protocol (CurveZMQ)
    
- `init_bls_keys`

    Initializes (or rotates) Node's BLS keys required for BLS multi-signature and State Proofs support 

- `read_ledger`

    Reads transaction from a specified ledger in JSON format
    
- `validator-info`

    Monitors the current status of the Node
    
- `generate_indy_pool_transactions`

    Initializes a test Pool (generates keys and genesis transactions)

- `clear_node`

    Clean up of all data on the Node 
