@echo off
set OMP_NUM_THREADS=16
set TOKENIZERS_PARALLELISM=false
"%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%~dp0train_distilbert.py" >> "%~dp0..\ai-engine\evaluation\distilbert_train.log" 2>&1
