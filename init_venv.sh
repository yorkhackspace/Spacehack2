#!/usr/bin/env bash
venv=venv
if [ -d $venv ]; then
    echo "Virtual environment already exists: $venv."
    echo "If you really want to reinitialise it, run 'rm -rf $venv' first."
    echo "If you just want to update the requirements, run 'pip install -r requirements.txt' with the venv activated"
    exit 1
fi
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
