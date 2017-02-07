@echo off

SET NODE_NAME=%1
SET NODE_PORT=%2
SET CLI_PORT=%3
SET USER=%4
SET PASSWORD=%5
SET RUN_MODE=%6
SET TEST_MODE=%7

IF NOT DEFINED NODE_NAME (
	echo "NODE_NAME argument is required"
  exit /B 1
)
IF NOT DEFINED NODE_PORT (
	echo "NODE_PORT argument is required"
  exit /B 1
)
IF NOT DEFINED CLI_PORT (
	echo "CLI_PORT argument is required"
  exit /B 1
)
)
IF NOT DEFINED USER (
	echo "USER argument is required"
  exit /B 1
)
)
IF NOT DEFINED PASSWORD (
	echo "PASSWORD argument is required"
  exit /B 1
)
IF DEFINED RUN_MODE (
	echo "RUN_MODE argument is %RUN_MODE%. Setting environment variable SOVRIN_NODE_PACKAGE_POSTFIX to %RUN_MODE%"
	SETX /m SOVRIN_NODE_PACKAGE_POSTFIX %RUN_MODE%
)
IF DEFINED TEST_MODE (
	echo "TEST_MODE argument is %TEST_MODE%. Setting environment variable TEST_MODE to %TEST_MODE%"
	SETX /m TEST_MODE %TEST_MODE%
)

FOR /f %%p in ('where python') do SET PYTHONPATH=%%p

SET CURR_DIR=%~dp0
echo "Creating service for agent"
nssm install SovrinNodeUpgradeAgent "%PYTHONPATH%"
nssm set SovrinNodeUpgradeAgent AppDirectory %CURR_DIR%
nssm set SovrinNodeUpgradeAgent AppParameters "%CURR_DIR%node_control_tool.py %TEST_MODE%"
echo "Creating service for node"
nssm install SovrinNode "%PYTHONPATH%"
nssm set SovrinNode AppDirectory %CURR_DIR%
nssm set SovrinNode AppParameters "%CURR_DIR%start_sovrin_node %NODE_NAME% %NODE_PORT% %CLI_PORT%"
nssm set SovrinNode DependOnService OrientDBGraph
nssm set SovrinNode ObjectName ".\%USER%" "%PASSWORD%"