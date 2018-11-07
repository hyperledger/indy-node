@echo off

SET NODE_NAME=%1
SET NODE_IP=%2
SET NODE_PORT=%3
SET CLI_IP=%4
SET CLI_PORT=%5
SET USER=%6
SET PASSWORD=%7
SET RUN_MODE=%8
SET TEST_MODE=%9

IF NOT DEFINED NODE_NAME (
	echo "NODE_NAME argument is required"
  exit /B 1
)
IF NOT DEFINED NODE_IP (
	echo "NODE_IP argument is required"
  exit /B 1
)
IF NOT DEFINED NODE_PORT (
	echo "NODE_PORT argument is required"
  exit /B 1
)
IF NOT DEFINED CLI_IP (
	echo "CLI_IP argument is required"
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
	echo "RUN_MODE argument is %RUN_MODE%. Setting environment variable INDY_NODE_PACKAGE_POSTFIX to %RUN_MODE%"
	SETX /m INDY_NODE_PACKAGE_POSTFIX %RUN_MODE%
)
IF DEFINED TEST_MODE (
	echo "TEST_MODE argument is %TEST_MODE%. Setting environment variable TEST_MODE to %TEST_MODE%"
	SETX /m TEST_MODE %TEST_MODE%
)

FOR /f %%p in ('where python') do SET PYTHONPATH=%%p

SET CURR_DIR=%~dp0
echo "Creating service for agent"
nssm install IndyNodeUpgradeAgent "%PYTHONPATH%"
nssm set IndyNodeUpgradeAgent AppDirectory %CURR_DIR%
nssm set IndyNodeUpgradeAgent AppParameters "%CURR_DIR%node_control_tool.py %TEST_MODE%"
echo "Creating service for node"
nssm install IndyNode "%PYTHONPATH%"
nssm set IndyNode AppDirectory %CURR_DIR%
nssm set IndyNode AppParameters "%CURR_DIR%start_indy_node %NODE_NAME% %NODE_IP% %NODE_PORT% %CLI_IP% %CLI_PORT%"
nssm set IndyNode ObjectName ".\%USER%" "%PASSWORD%"
echo "Creating agent restart task"
SchTasks /Create /TN RestartIndyNodeUpgradeAgent /TR "%CURR_DIR%restart_upgrade_agent.bat" /SC ONSTART /F