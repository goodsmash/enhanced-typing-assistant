@echo off
echo Setting up development environment...

:: Create Python virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

:: Install Node.js dependencies
echo Installing Node.js dependencies...
cd web
npm install

:: Start development servers
echo Starting development servers...
start cmd /k "cd web && npm start"
cd ..
start cmd /k "call venv\Scripts\activate && uvicorn typing_assistant.api.gender_inclusive_api:app --reload --host 0.0.0.0 --port 8000"

echo Development environment is ready!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
