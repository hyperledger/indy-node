@echo off

SET VERS=%1
IF NOT DEFINED VERS (
	echo "Version argument is required"
  exit /B 1
)

echo "Stopping node"
nssm stop IndyNode

echo "Run indy upgrade to version %VERS%"
pip install --upgrade --no-cache-dir indy-node%INDY_NODE_PACKAGE_POSTFIX%=="%VERS%"
SET RET=%ERRORLEVEL%
IF NOT "%RET%"=="0" (
  echo "Upgrade to version %VERS% failed %RET%"
)