# This script can be used when following the Indy_Running_Locally guide

stty sane

# Remove .indy folder
rm -rf ~/.indy

# Create nodes and generate initial transactions
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 2
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 3
generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 4

echo Environment setup complete
echo
echo "The nodes can be started using :"
echo
echo "start_indy_node Node1 9701 9702"
echo "start_indy_node Node2 9703 9704"
echo "start_indy_node Node3 9705 9706"
echo "start_indy_node Node4 9707 9708"
echo 
