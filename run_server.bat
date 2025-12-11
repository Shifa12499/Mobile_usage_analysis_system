@echo off
set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-8.0.472.8-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%
echo Starting FastAPI server with PySpark...
echo JAVA_HOME: %JAVA_HOME%
python -m uvicorn backend:app --reload --port 8000
