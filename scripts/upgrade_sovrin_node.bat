@echo off

SET VERS=%1
IF NOT DEFINED VERS (
	echo "Version argument is required"
  exit /B 1
)

echo "Stopping node"
nssm stop SovrinNode

echo "Backup pool_transactions_sandbox"
copy /y C:\Users\sovrin\.sovrin\pool_transactions_sandbox C:\Users\sovrin\.sovrin\pool_transactions_sandbox_backup

echo "Backup nssm"
copy /y C:\Users\sovrin\.sovrin\nssm.exe C:\Users\sovrin\.sovrin\nssm_backup.exe

echo "Run sovrin upgrade to version %VERS%"
pip install --upgrade --no-cache-dir plenum%SOVRIN_NODE_PACKAGE_POSTFIX% ledger%SOVRIN_NODE_PACKAGE_POSTFIX% sovrin-common%SOVRIN_NODE_PACKAGE_POSTFIX%
pip install --upgrade --no-cache-dir sovrin-node%SOVRIN_NODE_PACKAGE_POSTFIX%=="%VERS%"
set RET=%ERRORLEVEL%
IF NOT "%RET%"=="0" (
  echo "Upgrade to version %VERS% failed"
  exit /B 1
)

echo "Resotring pool_transactions_sandbox from backup"
copy /y C:\Users\sovrin\.sovrin\pool_transactions_sandbox_backup C:\Users\sovrin\.sovrin\pool_transactions_sandbox

echo "Resotring nssm from backup"
copy /y C:\Users\sovrin\.sovrin\nssm_backup.exe C:\Users\sovrin\.sovrin\nssm.exe

echo "Restarting node and agent"
nssm restart SovrinNodeUpgradeAgent
nssm start SovrinNode