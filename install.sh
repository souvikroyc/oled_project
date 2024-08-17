#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Retrieve the current username
USER_NAME=$(whoami)

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Git
sudo apt-get install -y git

# Install i2c-tools and python-smbus
sudo apt-get install -y i2c-tools python3-smbus

# Detect I2C devices (optional step for verification)
i2cdetect -y 1

# Install required system packages
sudo apt-get install -y python3-pip
sudo apt-get install -y libtiff-dev

# Remove EXTERNALLY-MANAGED file to allow pip package installation
sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install necessary Python packages
pip3 install luma.oled psutil

# Create the project directory if it doesn't exist
mkdir -p /home/$USER_NAME/oled_project

# Copy all project files to the project directory
cp -r * /home/$USER_NAME/oled_project/

# Set permissions and make the main script executable
chmod +x /home/$USER_NAME/oled_project/oled_stats.py

# Run the python code for display (optional for testing)
python3 /home/$USER_NAME/oled_project/oled_stats.py

# Create a systemd service to run the script on boot
sudo tee /etc/systemd/system/oled_stats.service > /dev/null <<EOF
[Unit]
Description=OLED Stats Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/$USER_NAME/oled_project/oled_stats.py
WorkingDirectory=/home/$USER_NAME/oled_project
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

echo "Setup completed. The OLED Stats script should be running."
