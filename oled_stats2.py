import time
import subprocess
import psutil
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw

# OLED setup
serial = i2c(port=1, address=0x3C)  # Adjust the I2C address if needed
device = ssd1306(serial, width=128, height=64)

# Load fonts
default_font = ImageFont.load_default()  # Small default font
ip_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)  # Larger font for IP

def get_ip_address():
    cmd = "hostname -I | cut -d' ' -f1"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024 * 1024 * 1024), mem.total / (1024 * 1024 * 1024)

def get_temperature():
    temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
    return temp.replace("temp=", "").strip()

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent, disk.used / (1024 * 1024 * 1024), disk.total / (1024 * 1024 * 1024)

# Main loop for displaying system stats
while True:
    ip_address = get_ip_address()
    cpu_usage = get_cpu_usage()
    memory_usage_percent, memory_used, memory_total = get_memory_usage()
    temperature = get_temperature()
    disk_usage_percent, disk_used, disk_total = get_disk_usage()

    with canvas(device) as draw:
        # Draw IP address with larger font
        draw.text((0, 0), f"IP: {ip_address}", font=ip_font, fill="yellow")
        
        # Combine CPU and Temperature on one line
        draw.text((0, 15), f"CPU: {cpu_usage}%  Temp: {temperature}", font=default_font, fill="blue")

        # Memory Usage in GB with percentage
        draw.text((0, 30), f"RAM: {memory_used:.2f}/{memory_total:.2f}GB ({memory_usage_percent}%)", font=default_font, fill="blue")
        
        # Disk Usage in GB with percentage
        draw.text((0, 45), f"Disk: {disk_used:.2f}/{disk_total:.2f}GB ({disk_usage_percent}%)", font=default_font, fill="blue")

    time.sleep(1)
