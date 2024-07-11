#!/bin/bash

# Check if python3 and pip are installed
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Please install Python3 to continue."
    exit 1
fi

if ! command -v pip &>/dev/null; then
    echo "pip is not installed. Please install pip to continue."
    exit 1
fi

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# Install psycopg2
pip install psycopg2-binary

python populate_db.py

deactivate