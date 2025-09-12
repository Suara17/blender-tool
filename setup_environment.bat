@echo off
echo Setting up Blender Dataset Generator environment...

# Create virtual environment
echo Creating virtual environment...
python -m venv venv

# Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

# Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

# Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete! To run the application:
echo 1. Activate the environment: venv\Scripts\activate
echo 2. Run the GUI: python blender_dataset_gui.py
echo.
echo Press any key to exit...
pause > nul