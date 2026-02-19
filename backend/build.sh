#!/usr/bin/env bash
# Render build script
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create data directory for SQLite
mkdir -p /opt/render/project/src/data
