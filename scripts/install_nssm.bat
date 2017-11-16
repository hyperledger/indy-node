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

echo "Installing nssm"
copy /y C:\Users\indy\.indy\nssm_original.exe C:\Users\indy\.indy\nssm.exe
SET Key="HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
FOR /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') DO (
    IF [%%b]==[] (
        SETX /m PATH "%%~a;%USERPROFILE%\.indy"
    ) ELSE (
        SETX /m PATH "%%~a %%~b;%USERPROFILE%\.indy"
    )
)