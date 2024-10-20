import time
import psutil
import socket
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
from PIL import ImageFont

# Define display parameters
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# Use default PIL font
font = ImageFont.load_default()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = 'N/A'
    finally:
        s.close()
    return ip

def get_temperature():
    temperatures = psutil.sensors_temperatures()
    if not temperatures:
        return 'N/A'
    for name, entries in temperatures.items():
        for entry in entries:
            return int(entry.current)  # Convert to integer
    return 'N/A'

while True:
    with canvas(device) as draw:
        # Fetch system information
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        temp = get_temperature()
        uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - psutil.boot_time()))
        disk = psutil.disk_usage('/').percent
        ip = get_ip_address()
        current_time = time.strftime('%Y-%m-%d %I:%M %p')

        # Draw lines at the top and bottom
        draw.line((0, 12, 128, 12), fill=255)
        draw.line((0, 49, 128, 49), fill=255)

        # Display system information
        draw.text((0, 0), f'IP: {ip}', font=font, fill=255)
        draw.text((0, 14), f'CPU: {cpu}%', font=font, fill=255)
        draw.text((64, 14), f'RAM: {ram}%', font=font, fill=255)
        draw.text((0, 26), f'Disk: {disk}%', font=font, fill=255)
        draw.text((64, 26), f'Temp: {temp}°C', font=font, fill=255)
        draw.text((0, 38), f'Uptime: {uptime}', font=font, fill=255)
        
        # Display current date (left-aligned) and time (right-aligned) below the bottom line
        draw.text((0, 50), current_time[:10], font=font, fill=255)  # Date
        draw.text((80, 50), current_time[11:], font=font, fill=255)  # Time

    time.sleep(1)
