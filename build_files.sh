#!/bin/bash

# Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

echo "Running migrations..."
python3.9 manage.py migrate --noinput

echo "Collect static files..."
python3.9 manage.py collectstatic --noinput --clear