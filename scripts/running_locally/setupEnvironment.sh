# This script can be used when following the Indy_Running_Locally guide

stty sane

# Remove .indy folder
rm -rf ~/.indy

# Create nodes and generate initial transactions
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 --network local
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 2 --network local
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 3 --network local
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 4 --network local

echo Environment setup complete
echo
echo "The nodes can be started using :"
echo
echo "start_indy_node Node1 0.0.0.0 9701 0.0.0.0 9702"
echo "start_indy_node Node2 0.0.0.0 9703 0.0.0.0 9704"
echo "start_indy_node Node3 0.0.0.0 9705 0.0.0.0 9706"
echo "start_indy_node Node4 0.0.0.0 9707 0.0.0.0 9708"
echo 
