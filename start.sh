#!/usr/bin/bash

source env/bin/activate
chmod +x main.py
./main.py || exit $?

pip install youtube-dl --upgrade
