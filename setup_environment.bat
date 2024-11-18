@echo off
echo Setting up virtual environment and installing dependencies...

REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Install spacy model
python -m spacy download en_core_web_sm

echo Setup complete! The environment is now ready.
