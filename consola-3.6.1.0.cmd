@echo off
color 1E

set PYVER=36 
set APPS=%USERPROFILE%\Apps
set PYTRT=%APPS%\WinPython\3.6.1.0Qt5\python-3.6.1.amd64
set MGWRT=%APPS%\mingw64-6.3.0
set SCIRT=%APPS%\IDEs\wscite
set CODRT=%APPS%\IDEs\VSCode
set NODRT=%APPS%\node\7.10.0

set PATH=%PYTRT%;%PYTRT%\Scripts;%MGWRT%\bin;%SCIRT%;%CODRT%;%NODRT%;%PATH%
set PROMPT=CONSOLA 3.6.1 - $P$_$G
cmd
