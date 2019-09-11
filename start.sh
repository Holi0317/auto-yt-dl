#!/usr/bin/bash

set -e

# Setup virtual environment if not exist
if [ ! -d "env" ]; then
  python -m venv env
fi

source env/bin/activate
pip install -r requirements.txt --upgrade
pip install youtube-dl --upgrade

python main.py
