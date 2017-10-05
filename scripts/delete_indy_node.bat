@echo off
echo "Deleting service for agent"
sc delete "IndyNodeUpgradeAgent"
echo "Deleting service for node"
sc delete "IndyNode"
echo "Please reboot"