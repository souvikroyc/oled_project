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

### 1. Clone the Repository

First, clone this repository to your Raspberry Pi:

```bash
git clone https://github.com/souvikroyc/oled_project.git
cd oled_project

sudo apt-get install dos2unix
dos2unix install.sh

chmod +x install.sh
./install.sh


### 2. Reboot (if necessary)
After the script completes successfully, your Raspberry Pi should start displaying the stats on the OLED screen. If not, try rebooting:
```bash
sudo reboot

