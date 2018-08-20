# Add Node to Existing Pool

## Node preparation

1. Add this files from a running node:
```
/var/lib/indy/network_name/pool_transactions_genesis
/var/lib/indy/network_name/domain_transactions_genesis
```

2. Initialize keys, aliases and ports on the new node using init_indy_node script.
Example:
```
sudo su - indy -c "init_indy_node NewNode 0.0.0.0 9701 0.0.0.0 9702 0000000000000000000000000NewNode"
```

3. When the node starts for the first time, it reads the content of genesis `pool_transactions_sandbox` and `domain_transactions_sandbox` files and adds it to the ledger. The Node reads genesis transactions only once during the first start-up, so make sure the genesis files are correct before starting the service.
```
sudo systemctl start indy-node
sudo systemctl status indy-node
sudo systemctl enable indy-node
```

## Add Node to the Pool

1. As Trustee add another Steward if needed (only Steward can add a new Validator Node; a Steward can add one and only one Validator Node).
2. Using Indy CLI, run the following command as Steward:
```
ledger node target=6G9QhQa3HWjRKeRmEvEkLbWWf2t7cw6KLtafzi494G4G client_port=9702 client_ip=10.255.255.255 alias=NewNode node_ip=10.0.0.10.255.255.255 node_port=9701 services=VALIDATOR blskey=zi65fRHZjK2R8wdJfDzeWVgcf9imXUsMSEY64LQ4HyhDMsSn3Br1vhnwXHE7NyGjxVnwx4FGPqxpzY8HrQ2PnrL9tu4uD34rjgPEnFXnsGAp8aF68R4CcfsmUXfuU51hogE7dZCvaF9GPou86EWrTKpW5ow3ifq16Swpn5nKMXHTKj blskey_pop=RaY9xGLbQbrBh8np5gWWQAWisaxd96FtvbxKjyzBj4fUYyPq4pkyCHTYvQzjehmUK5pNfnyhwWqGg1ahPwtWopenuRjAeCbib6sVq68cTBXQfXv5vTDhWs6AmdQBcYVELFpyGba9G6CfqQ5jnkDiaAm2PyBswJxpu6AZTxKADhtSrj
```
- `alias` specifies unique Node name
- `target` specifies public key from `init_indy_node` script
- `blskey` specifies BLS key from `init_indy_node` script
- `blskey_pop` specifies Proof of possession for BLS key from `init_indy_node` script

## Make sure that Node is workable

Do `systemctl restart indy-node` and verify that node completed catch-up successfully.
 