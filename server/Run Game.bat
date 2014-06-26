@ECHO off
cd src
set /p PORT="IP Port: "
if "%PORT%"=="" (set PORT="8007")
server.py %PORT%
PAUSE