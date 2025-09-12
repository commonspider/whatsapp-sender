#!/bin/sh

cd "$(dirname "$0")"
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
