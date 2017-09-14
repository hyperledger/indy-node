@echo off
echo "Deleting service for agent"
sc delete "SovrinNodeUpgradeAgent"
echo "Deleting service for node"
sc delete "SovrinNode"
echo "Please reboot"