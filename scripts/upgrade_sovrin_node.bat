@echo off

SET VERS=%1
IF NOT DEFINED VERS (
	echo "Version argument is required"
  exit /B 1
)

echo "Stopping node"
nssm stop SovrinNode

echo "Run sovrin dependecies upgrade"
pip install --upgrade --no-cache-dir plenum%SOVRIN_NODE_PACKAGE_POSTFIX% ledger%SOVRIN_NODE_PACKAGE_POSTFIX% sovrin-common%SOVRIN_NODE_PACKAGE_POSTFIX%
SET RET=%ERRORLEVEL%
IF NOT "%RET%"=="0" (
  echo "Upgrade of dependecies failed %RET%"
)
echo "Run sovrin upgrade to version %VERS%"
pip install --upgrade --no-cache-dir sovrin-node%SOVRIN_NODE_PACKAGE_POSTFIX%=="%VERS%"
SET RET=%ERRORLEVEL%
IF NOT "%RET%"=="0" (
  echo "Upgrade to version %VERS% failed %RET%"
)

echo "Restarting node and agent"
nssm start SovrinNode
schtasks /run /TN "RestartSovrinNodeUpgradeAgent"