import time
import subprocess
import psutil
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
welcome_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)

def display_welcome_message():
    with canvas(device) as draw:
        welcome_message = "Getting Info..."
        # Correct width/height calculation
        x0, y0, x1, y1 = draw.textbbox((0, 0), welcome_message, font=welcome_font)
        text_width  = x1 - x0
        text_height = y1 - y0
        text_x = (device.width - text_width) // 2
        text_y = (device.height - text_height) // 2
        draw.text((text_x, text_y), welcome_message, font=welcome_font, fill="white")
    time.sleep(10)

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
        # raw looks like "temp=47.8'C\n"
        celsius = float(raw.split('=')[1].split("'")[0])
        fahrenheit = celsius * 9 / 5 + 32
        return f"{fahrenheit:.1f}°F"
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return "N/A"

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent, disk.used / (1024 * 1024 * 1024), disk.total / (1024 * 1024 * 1024)

# Show welcome screen
display_welcome_message()

try:
    while True:
        ip_address = get_ip_address()
        cpu_usage = get_cpu_usage()
        mem_percent, mem_used, mem_total = get_memory_usage()
        temperature_f = get_temperature_f()
        disk_percent, disk_used, disk_total = get_disk_usage()

        with canvas(device) as draw:
            draw.text((0, 0), "Raspberry Pi Stats:", font=ip_font, fill="white")
            draw.text((0, 15), f"CPU:{cpu_usage:.1f}% Temp:{temperature_f}", font=default_font, fill="white")
            draw.text((0, 30), f"RAM:{mem_used:.2f}/{mem_total:.2f}GB", font=default_font, fill="white")
            draw.text((0, 45), f"Disk:{disk_used:.2f}/{disk_total:.2f}GB", font=default_font, fill="white")
            draw.text((0, 60), f"IP: {ip_address}", font=default_font, fill="white")

        time.sleep(1)

except KeyboardInterrupt:
    device.clear()



