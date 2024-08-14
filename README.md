# oled_project_files
Repository for OLED project files including fonts and scripts


1. Using Systemd Service
Systemd is the most modern and versatile way to manage services on Linux systems, including the Raspberry Pi. Here’s how to set it up:

Step-by-Step Setup
Create a Systemd Service File

Create a new service file for your script:

<code> sudo nano /etc/systemd/system/oled_display.service </code>

Add Service Configuration

Add the following configuration to the file:


  
<code> [Unit]
Description=OLED Display Service
After=network.target </code>

<code>[Service]
ExecStart=/usr/bin/python3 /home/pi/oled_project/oled_display.py
WorkingDirectory=/home/pi/oled_project
User=pi
Group=pi
Restart=always
RestartSec=5</code>

<code>[Install]
WantedBy=multi-user.target </code>


ExecStart: Specifies the command to run your script. Ensure /usr/bin/python3 is the correct path to Python 3 on your system.
WorkingDirectory: Specifies the directory where your script resides.
Restart=always: Ensures the script restarts if it fails.
RestartSec=5: Waits 5 seconds before restarting.
Reload Systemd to Recognize the New Service

bash
Copy code
sudo systemctl daemon-reload
Enable the Service to Start on Boot

bash
Copy code
sudo systemctl enable oled_display.service
Start the Service

bash
Copy code
sudo systemctl start oled_display.service
Check Service Status

You can check if your service is running with:

bash
Copy code
sudo systemctl status oled_display.service
