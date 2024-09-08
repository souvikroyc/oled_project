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
chmod +x "$PROJECT_DIR/oled_stats2.py"

# Create a systemd service to run the script on boot
sudo tee /etc/systemd/system/oled_stats.service > /dev/null <<EOF
[Unit]
Description=OLED Stats Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $PROJECT_DIR/oled_stats2.py
WorkingDirectory=$PROJECT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER_NAME

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to apply the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable oled_stats.service

# Start the service immediately
sudo systemctl start oled_stats.service

echo "Setup completed. The OLED Stats script is set to run at startup via systemd."
