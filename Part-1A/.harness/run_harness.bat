@echo off
setlocal

ruff check .
if errorlevel 1 exit /b %errorlevel%

bandit -r src
if errorlevel 1 exit /b %errorlevel%

pytest
exit /b %errorlevel%
