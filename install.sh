#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Retrieve the current username
USER_NAME=$(whoami)

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Git and necessary packages
sudo apt-get install -y git i2c-tools python3-smbus python3-pip libtiff-dev

# Detect I2C devices (optional step for verification)
i2cdetect -y 1

# Remove EXTERNALLY-MANAGED file to allow pip package installation
sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install necessary Python packages
pip3 install luma.oled psutil

# Create the project directory if it doesn't exist
PROJECT_DIR="/home/$USER_NAME/oled_project"
mkdir -p "$PROJECT_DIR"

# Copy all project files to the project directory
cp -r * "$PROJECT_DIR/"

# Set permissions and make the main script executable
chmod +x "$PROJECT_DIR/oled_stats.py"

# Run the python code for display (optional for testing)
python3 "$PROJECT_DIR/oled_stats.py"

# Add a cron job to run the script at reboot
CRON_JOB="@reboot /usr/bin/python3 $PROJECT_DIR/oled_stats.py"
(crontab -l ; echo "$CRON_JOB") | crontab -

echo "Setup completed. The OLED Stats script is set to run at startup via cron."
sudo reboot
