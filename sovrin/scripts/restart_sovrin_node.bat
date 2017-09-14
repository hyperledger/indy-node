@echo off

echo "Restarting node and agent"
nssm start SovrinNode
schtasks /run /TN "RestartSovrinNodeUpgradeAgent"