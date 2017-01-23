@echo off

echo "Installing nssm"
SET Key="HKCU\Environment"
FOR /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH') DO (
    IF [%%b]==[] (
        SETX PATH "%%~a;%USERPROFILE%\.sovrin"
    ) ELSE (
        SETX PATH "%%~a %%~b;%USERPROFILE%\.sovrin"
    )
)