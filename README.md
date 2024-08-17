# OLED Stats Display for Raspberry Pi

This project displays system stats (IP address, CPU usage, RAM usage, temperature, and storage usage) on a 0.96-inch OLED screen connected to a Raspberry Pi. The display is driven by the `luma.oled` library, which is compatible with the Raspberry Pi 5.

## Features

- **IP Address**: Displays the current IP address of the Raspberry Pi.
- **CPU Usage**: Shows the CPU usage percentage.
- **RAM Usage**: Displays the current RAM usage along with the percentage.
- **Temperature**: Displays the CPU temperature in Celsius.
- **Storage Usage**: Shows the total and used storage with the usage percentage.

## Hardware Requirements

- **Raspberry Pi 5** with Raspberry Pi OS 64-bit Lite installed
- **0.96-inch OLED Display** (128x64 resolution, with top line yellow and remaining blue text)
- **I2C Interface** enabled on the Raspberry Pi

## Software Requirements

- **Python 3** (already included with Raspberry Pi OS)
- **Git** for cloning the repository
- **I2C-tools** for detecting the OLED display

## Installation

### 1. Enable I2C on Your Raspberry Pi 5

Open the Raspberry Pi configuration tool:

<code>sudo raspi-config</code>

Navigate to Interfacing Options and enable I2C.

### 2. Install Git (if using Lite OS)
If you are using Raspberry Pi OS Lite, you need to install Git:

<code>sudo apt-get update
sudo apt-get install -y git</code>

### 3. Download Repository from GitHub
Clone the repository and navigate to the project directory:

<code>git clone https://github.com/souvikroyc/oled_project.git
cd oled_project</code>

### 4. Execute the Installation Script
Convert line endings of the install.sh script to Unix format and make it executable:

<code>sudo apt-get install -y dos2unix
dos2unix install.sh
chmod +x install.sh</code>

Run the installation script:

<code>./install.sh</code>

### 5. Reboot (if necessary)
After the script completes successfully, your Raspberry Pi should start displaying the stats on the OLED screen. If not, try rebooting:

<code>sudo reboot</code>

## Troubleshooting

ModuleNotFoundError: No module named 'psutil': Install psutil using 
<code>pip3 install psutil</code>
ModuleNotFoundError: No module named 'luma': Install luma.oled using 
<code>pip3 install luma.oled</code>
No output on OLED display: Ensure the I2C interface is enabled and that the OLED display is correctly wired and detected (<code>i2cdetect -y 1</code>).
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contributing
Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

Acknowledgements
This project uses the luma.oled library for handling the OLED display and psutil for system stats.
