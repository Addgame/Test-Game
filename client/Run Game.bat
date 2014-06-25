@ECHO off
cd src
set /p NAME="Player Name: "
if "%NAME%"=="" (set NAME="player")
set /p IP="IP Address: "
if "%IP%"=="" (set IP="localhost")
set /p PORT="IP Port: "
if "%PORT%"=="" (set PORT="8007")
client.py %NAME% %IP% %PORT%
PAUSE