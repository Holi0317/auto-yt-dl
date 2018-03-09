#!/usr/bin/bash

pipenv update youtube-dl

pipenv run python main.py || exit $?
