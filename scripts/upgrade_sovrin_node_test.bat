@echo off

SET VERS=%1
IF NOT DEFINED VERS (
	echo "Version argument is required"
  exit /B 1
)

echo "Run sovrin upgrade to version %VERS%"
pip install --upgrade plenum%SOVRIN_NODE_PACKAGE_POSTFIX% ledger%SOVRIN_NODE_PACKAGE_POSTFIX% sovrin-common%SOVRIN_NODE_PACKAGE_POSTFIX%
pip install --upgrade sovrin-node%SOVRIN_NODE_PACKAGE_POSTFIX%=="%VERS%"
set RET=%ERRORLEVEL%
IF NOT "%RET%"=="0" (
  echo "Upgrade to version %VERS% failed"
  exit /B 1
)

echo "Restarting node and agent"
sc stop SovrinNodeUpgradeAgent && sc start SovrinNodeUpgradeAgent
sc stop SovrinNode && sc start SovrinNode