#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
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
echo "start_indy_node Node1 9701 9702"
echo "start_indy_node Node2 9703 9704"
echo "start_indy_node Node3 9705 9706"
echo "start_indy_node Node4 9707 9708"
echo 
