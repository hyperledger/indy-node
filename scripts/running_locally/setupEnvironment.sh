# This script can be used when following the Sovrin_Running_Locally guide

# reset database
/opt/orientdb/bin/console.sh < resetDB.sql
stty sane

# Remove .sovrin folder
rm -rf ~/.sovrin

# Create nodes and generate initial transactions
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 1
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 2
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 3
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 4

echo Environment setup complete
echo
echo "The nodes can be started using :"
echo
echo "start_sovrin_node Node1 9701 9702"
echo "start_sovrin_node Node2 9703 9704"
echo "start_sovrin_node Node3 9705 9706"
echo "start_sovrin_node Node4 9707 9708"
echo 
