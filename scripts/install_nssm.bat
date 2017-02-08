@echo off

echo "Installing nssm"
copy /y C:\Users\sovrin\.sovrin\nssm_original.exe C:\Users\sovrin\.sovrin\nssm.exe
SET Key="HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
FOR /f "skip=2 tokens=3*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') DO (
    IF [%%b]==[] (
        SETX /m PATH "%%~a;%USERPROFILE%\.sovrin"
    ) ELSE (
        SETX /m PATH "%%~a %%~b;%USERPROFILE%\.sovrin"
    )
)