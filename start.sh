#!/usr/bin/bash

source env/bin/activate
chmod +x main.py
pip install youtube-dl pip --upgrade

./main.py || exit $?
