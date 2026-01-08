@echo off
:: Consolidated Background Run Script
:: Usage: run_background.bat [count]
:: Default count is 50 if no argument is provided.

set "INSCRIPTIONS=%~1"
if "%INSCRIPTIONS%"=="" set "INSCRIPTIONS=50"

echo [AGKI] Starting background tagging for %INSCRIPTIONS% inscriptions...
echo [AGKI] Logging output to data\logs\background_run.log

set MAX_INSCRIPTIONS=%INSCRIPTIONS%
python -m source.main >> data\logs\background_run.log 2>&1

echo [AGKI] Process finished.