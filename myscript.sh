#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate the virtual environment
source ./venv/Scripts/activate

# Run the Python script
python ./naukri.py
