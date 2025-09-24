import time
import subprocess
import psutil
import glob                 # NEW: for finding the fan speed file
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# OLED setup
serial = i2c(port=1, address=0x3C)  # Adjust the I2C address if needed
device = ssd1306(serial, width=128, height=64)

# Load fonts
default_font = ImageFont.load_default()
ip_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)

def get_ip_address():
    cmd = "hostname -I | cut -d' ' -f1"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

def get_cpu_usage():
    return psutil.cpu_percent(interval=0.5)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024 * 1024 * 1024), mem.total / (1024 * 1024 * 1024)

def get_temperature_f():
    """Return CPU temperature in Fahrenheit as a string like '120.3°F'."""
    try:
        raw = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        celsius = float(raw.split('=')[1].split("'")[0])
        fahrenheit = celsius * 9 / 5 + 32
        return f"{fahrenheit:.1f}°F"
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return "N/A"

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent, disk.used / (1024 * 1024 * 1024), disk.total / (1024 * 1024 * 1024)

def get_fan_speed():
    """
    Return built-in Raspberry Pi 5 fan speed in RPM.
    Looks for /sys/devices/platform/cooling_fan/hwmon*/fan1_input.
    """
    try:
        paths = glob.glob("/sys/devices/platform/cooling_fan/hwmon*/fan1_input")
        if not paths:
            return "N/A"
        with open(paths[0], "r") as f:
            rpm = int(f.read().strip())
        return f"{rpm} RPM"
    except (FileNotFoundError, ValueError, PermissionError):
        return "N/A"

try:
    while True:
        ip_address = get_ip_address()
        cpu_usage = get_cpu_usage()
        mem_percent, mem_used, mem_total = get_memory_usage()
        temperature_f = get_temperature_f()
        disk_percent, disk_used, disk_total = get_disk_usage()
        fan_speed = get_fan_speed()                 # NEW

        with canvas(device) as draw:
            draw.text((0, 0),  "Raspberry Pi Stats:", font=ip_font, fill="white")
            draw.text((0, 10), f"CPU:{cpu_usage:.1f}% Temp:{temperature_f}", font=default_font, fill="white")
            draw.text((0, 21), f"RAM:{mem_used:.2f}/{mem_total:.2f}GB",      font=default_font, fill="white")
            draw.text((0, 32), f"Disk:{disk_used:.2f}/{disk_total:.2f}GB",   font=default_font, fill="white")
            draw.text((0, 43), f"Fan: {fan_speed}",                          font=default_font, fill="white")
            draw.text((0, 54), f"IP: {ip_address}",                          font=default_font, fill="white")

        time.sleep(1)

except KeyboardInterrupt:
    device.clear()



