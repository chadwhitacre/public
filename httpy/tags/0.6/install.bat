@ECHO OFF
REM This script installs httpy.

cls
ECHO.
ECHO INSTALLING HTTPY ...

:: Install into python
ECHO.
ECHO installing python package
ECHO ===============================================================================
python setup.py install
if not errorlevel 1 goto pyfound
ECHO error installing python package -- do you have python?
goto end

:: Remove any old installation
:pyfound
if not exist "%PROGRAMFILES%\httpy" goto copy
ECHO.
ECHO.
ECHO removing old installation
ECHO ===============================================================================
if exist "%SYSTEMROOT%\httpy.bat" del "%SYSTEMROOT%\httpy.bat" /q
rmdir /s /q "%PROGRAMFILES%\httpy"

:: Install the executable
:copy
ECHO.
ECHO.
ECHO installing executable
ECHO ===============================================================================
mkdir "%PROGRAMFILES%\httpy"
copy bin\httpy.py "%PROGRAMFILES%\httpy\httpy"


:: Install a proxy executable along PATH
ECHO.
ECHO.
ECHO installing proxy executable
ECHO ===============================================================================
>  %SYSTEMROOT%\httpy.bat ECHO @echo off
>> %SYSTEMROOT%\httpy.bat ECHO python "%PROGRAMFILES%\httpy\httpy"


ECHO.
ECHO ... INSTALLATION COMPLETE
ECHO.
ECHO To confirm that httpy is successfully installed, type 'httpy' at a command
ECHO prompt and hit ^<enter^>, like this:
ECHO.
ECHO     C:\Documents and Settings\whit537\httpy^>httpy
ECHO     1  httpy started on port 8080
ECHO.
ECHO Then visit http://localhost:8080/ in a web browser. Use ^<ctrl-C^> to
ECHO stop httpy. Note that it can sometimes take a second to shutdown, and
ECHO you will get a prompt to terminate a batch file; just answer Yes.
ECHO.

:end
pause