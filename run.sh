#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python slsah.py
read -p "Press Enter to exit"

