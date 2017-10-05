@echo off

echo "Restarting node and agent"
nssm start IndyNode
schtasks /run /TN "RestartIndyNodeUpgradeAgent"