#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python generate_schema_from_api.py
read -p "Press Enter to exit"
