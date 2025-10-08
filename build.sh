#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install FFmpeg (required for audio conversion)
apt-get update
apt-get install -y ffmpeg

# Create downloads directory
mkdir -p downloads
