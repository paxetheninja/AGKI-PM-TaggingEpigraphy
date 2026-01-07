@echo off
set MAX_INSCRIPTIONS=3
python -m source.main >> data\logs\background_run.log 2>&1
