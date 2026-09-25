#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Finz: Installing Dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Finz: Running Database Migrations ==="
python frontend/manage.py migrate --no-input

echo "=== Finz: Collecting Static Files ==="
python frontend/manage.py collectstatic --no-input

echo "=== Finz: Build Complete ==="
