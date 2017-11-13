::   Copyright 2017 Sovrin Foundation
::
::   Licensed under the Apache License, Version 2.0 (the "License");
::   you may not use this file except in compliance with the License.
::   You may obtain a copy of the License at
::
::       http://www.apache.org/licenses/LICENSE-2.0
::
::   Unless required by applicable law or agreed to in writing, software
::   distributed under the License is distributed on an "AS IS" BASIS,
::   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
::   See the License for the specific language governing permissions and
::   limitations under the License.
::

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

echo "Restarting node and agent"
nssm start IndyNode
schtasks /run /TN "RestartIndyNodeUpgradeAgent"