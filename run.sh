#!/bin/bash
cd "$(dirname "$0")"
if [ -x ./venv/bin/python ]; then
  ./venv/bin/python main.py "$@"
elif [ -x ./venv/Scripts/python.exe ]; then
  ./venv/Scripts/python.exe main.py "$@"
else
  python main.py "$@"
fi
