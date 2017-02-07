@echo off

echo "Installing nssm"
copy /y C:\Users\sovrin\.sovrin\nssm_original.exe C:\Users\sovrin\.sovrin\nssm.exe
SET Key="HKCU\Environment"
FOR /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH') DO (
    IF [%%b]==[] (
        SETX PATH "%%~a;%USERPROFILE%\.sovrin"
    ) ELSE (
        SETX PATH "%%~a %%~b;%USERPROFILE%\.sovrin"
    )
)