#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Git
sudo apt-get install -y git

# Install i2c-tools and python-smbus
sudo apt-get install -y i2c-tools python3-smbus

# Enable I2C by modifying the config.txt file
# Add i2c-bcm2708 and i2c-dev modules to /boot/config.txt
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "Enabling I2C in /boot/config.txt"
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

# Detect I2C devices (optional step for verification)
i2cdetect -y 1

# Install required system packages
sudo apt-get install -y python3-pip python3-dev python3-setuptools libjpeg-dev \
zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 libatlas-base-dev

# Remove EXTERNALLY-MANAGED file to allow pip package installation
sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install necessary Python packages
pip3 install luma.oled psutil

# Create the project directory if it doesn't exist
mkdir -p /home/pi/oled_project

# Copy all project files to the project directory
cp -r * /home/pi/oled_project/

# Set permissions and make the main script executable
chmod +x /home/pi/oled_project/oled_stats.py

# Create a systemd service to run the script on boot
sudo tee /etc/systemd/system/oled_stats.service > /dev/null <<EOF
[Unit]
Description=OLED Stats Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/oled_project/oled_stats.py
WorkingDirectory=/home/pi/oled_project
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

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
