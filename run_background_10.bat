@echo off
set MAX_INSCRIPTIONS=10
python -m source.main >> data\logs\background_run_10.log 2>&1
