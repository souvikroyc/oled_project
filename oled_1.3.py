import time
import subprocess
import psutil
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
# Your external drive mount point.
# Use 'df -h' command in terminal to find it. Example: /media/pi/MyUSB
EXTERNAL_DRIVE_PATH = "/media/pi/MY_USB_DRIVE" # <--- CHANGE THIS

# --- Display Setup ---
try:
    # Initialize I2C interface. The port is 1 for most Raspberry Pi models.
    serial = i2c(port=1, address=0x3C)
    # Initialize the SH1106 OLED device.
    # The resolution for most 1.3" displays is 128x64.
    device = sh1106(serial, rotate=0) # Set rotate to 2 if display is upside down
    # Load a small, readable font. Default font is small.
    # To use a custom font, provide the path: font = ImageFont.truetype("path/to/font.ttf", size)
    font = ImageFont.load_default()
    # You can use a slightly larger font for titles if you wish
    font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)

except Exception as e:
    print(f"Error initializing display: {e}")
    print("Please ensure I2C is enabled and the display is connected correctly.")
    exit()


# --- Helper Functions to Get System Info ---

def get_ip_address():
    """Gets the primary IP address of the Pi."""
    try:
        ip = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
        return ip
    except Exception:
        return "N/A"

def get_cpu_info():
    """Returns CPU usage percentage, speed in MHz, and temperature."""
    cpu_usage = psutil.cpu_percent(interval=1)
    # On Pi 5, current frequency is more reliable.
    try:
        cpu_freq_info = psutil.cpu_freq()
        cpu_speed = f"{cpu_freq_info.current:.0f}MHz"
    except Exception:
        cpu_speed = "N/A"
    
    # Read CPU temperature
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_raw = int(f.read().strip())
        cpu_temp = f"{temp_raw / 1000.0:.1f}°C"
    except FileNotFoundError:
        cpu_temp = "N/A"
        
    return cpu_usage, cpu_speed, cpu_temp

def get_ram_info():
    """Returns RAM usage percentage and remaining MB."""
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    ram_remaining = f"{ram.available / (1024*1024):.0f}MB"
    return ram_usage, ram_remaining

def get_storage_info(path):
    """Returns storage usage percentage and free GB for a given path."""
    try:
        storage = psutil.disk_usage(path)
        storage_usage = storage.percent
        storage_free = f"{storage.free / (1024*1024*1024):.1f}GB"
        return storage_usage, storage_free
    except FileNotFoundError:
        return 0, "N/A"

def get_fan_speed():
    """Returns the fan speed in RPM if available."""
    # This is a common path for the official Pi 5 fan controller.
    # It might be different for third-party fans.
    try:
        with open('/sys/class/thermal/cooling_device0/cur_state', 'r') as f:
            # The value often corresponds to a speed level, not direct RPM.
            # This logic might need adjustment based on your fan.
            # For the official fan, it's often 0-4.
            speed_level = int(f.read().strip())
            # A simple representation. You might need a more complex mapping.
            return f"Lvl {speed_level}"
    except (FileNotFoundError, ValueError):
        return "N/A"

def draw_bar(draw, x, y, width, height, percentage, label):
    """Draws a horizontal progress bar with a label."""
    # Draw border
    draw.rectangle((x, y, x + width, y + height), outline="white", fill="black")
    # Draw filled part
    fill_width = int((percentage / 100.0) * (width - 2))
    draw.rectangle((x + 1, y + 1, x + 1 + fill_width, y + height - 1), outline="white", fill="white")
    # Draw label
    draw.text((x + width + 5, y), label, font=font_small, fill="white")


# --- Main Loop to Draw the Dashboard ---
def main():
    screen_index = 0
    while True:
        # --- Screen 1: Overview (IP, CPU, RAM) ---
        if screen_index == 0:
            ip_addr = get_ip_address()
            cpu_usage, _, cpu_temp = get_cpu_info()
            ram_usage, _ = get_ram_info()

            with canvas(device) as draw:
                # Title
                draw.text((0, 0), "SYSTEM OVERVIEW", font=font_bold, fill="white")
                draw.line((0, 13, 128, 13), fill="white")

                # IP Address
                draw.text((0, 18), f"[i] IP: {ip_addr}", font=font_small, fill="white")
                
                # CPU Info
                draw.text((0, 32), f"[C] CPU: {cpu_temp}", font=font_small, fill="white")
                draw_bar(draw, 45, 33, 40, 8, cpu_usage, f"{cpu_usage}%")
                
                # RAM Info
                draw.text((0, 46), f"[R] RAM:", font=font_small, fill="white")
                draw_bar(draw, 45, 47, 40, 8, ram_usage, f"{ram_usage}%")


        # --- Screen 2: Detailed Performance ---
        elif screen_index == 1:
            _, cpu_speed, cpu_temp = get_cpu_info()
            _, ram_remaining = get_ram_info()
            fan_speed = get_fan_speed()

            with canvas(device) as draw:
                # Title
                draw.text((0, 0), "PERFORMANCE", font=font_bold, fill="white")
                draw.line((0, 13, 128, 13), fill="white")

                draw.text((0, 18), f"CPU Temp: {cpu_temp}", font=font_small, fill="white")
                draw.text((0, 30), f"CPU Speed: {cpu_speed}", font=font_small, fill="white")
                draw.text((0, 42), f"Fan Speed: {fan_speed}", font=font_small, fill="white")
                draw.text((0, 54), f"RAM Free: {ram_remaining}", font=font_small, fill="white")


        # --- Screen 3: Storage Details ---
        elif screen_index == 2:
            root_usage, root_free = get_storage_info('/')
            ext_usage, ext_free = get_storage_info(EXTERNAL_DRIVE_PATH)

            with canvas(device) as draw:
                # Title
                draw.text((0, 0), "STORAGE", font=font_bold, fill="white")
                draw.line((0, 13, 128, 13), fill="white")
                
                # Root (microSD card) Storage
                draw.text((0, 18), "OS (microSD):", font=font_small, fill="white")
                draw_bar(draw, 5, 30, 70, 9, root_usage, f"{root_free} free")
                
                # External Drive Storage
                draw.text((0, 44), "External Drive:", font=font_small, fill="white")
                draw_bar(draw, 5, 56, 70, 9, ext_usage, f"{ext_free} free")


        # Cycle to the next screen
        screen_index = (screen_index + 1) % 3
        time.sleep(5) # Screen refresh interval

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Dashboard stopped.")
