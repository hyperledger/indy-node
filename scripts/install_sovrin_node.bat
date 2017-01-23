@echo off

SET NODE_NAME=%1
SET NODE_PORT=%2
SET CLI_PORT=%3

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

FOR /f %%p in ('where python') do SET PYTHONPATH=%%p

SET CURR_DIR=%~dp0
echo "Creating service for agent"
nssm install SovrinNodeUpgradeAgent "%PYTHONPATH%"
nssm set SovrinNodeUpgradeAgent AppDirectory %CURR_DIR%
nssm set SovrinNodeUpgradeAgent AppParameters "%CURR_DIR%node_control_tool.py"
echo "Creating service for node"
nssm install SovrinNode "%PYTHONPATH%"
nssm set SovrinNode AppDirectory %CURR_DIR%
nssm set SovrinNode AppParameters "%CURR_DIR%start_sovrin_node %NODE_NAME% %NODE_PORT% %CLI_PORT%"