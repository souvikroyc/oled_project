#!/bin/bash

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pip python3-dev python3-setuptools libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libatlas-base-dev

# Install Python packages
pip3 install luma.oled psutil

# Create a directory for the project
mkdir -p /home/pi/oled_project

# Copy the script and any other necessary files
cp -r * /home/pi/oled_project/

# Set permissions and make the script executable
chmod +x /home/pi/oled_project/oled_stats.py

# Create a systemd service to run the script on boot
cat <<EOF | sudo tee /etc/systemd/system/oled_stats.service
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

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable oled_stats.service
sudo systemctl start oled_stats.service

echo "Setup completed. The OLED Stats script should be running."
