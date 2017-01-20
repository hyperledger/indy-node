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
IF NOT DEFINED PYTHONPATH (
	echo "Python must be in your path"
  exit /B 1
)

SET CURR_DIR=%~dp0
echo "Deleting old services"
sc delete "SovrinNodeUpgradeAgent"
sc delete "SovrinNode"
echo "Creating service for agent"
sc create "SovrinNodeUpgradeAgent" binPath= "%PYTHONPATH% %CURR_DIR%node_control_tool.py" start=auto
echo "Creating service for node"
sc create "SovrinNode" binPath= "%PYTHONPATH% %CURR_DIR%start_sovrin_node %NODE_NAME% %NODE_PORT% %CLI_PORT%" start=auto