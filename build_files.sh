#!/bin/bash

# Build the project
echo "Building the project..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collect static files..."
python manage.py collectstatic --noinput --clear