import time
import subprocess
import psutil
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import config  # Assuming your API key and city are stored in config.py
import math

# Initialize the display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

# Load fonts
default_font = ImageFont.load_default()  # Small default font
ip_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)  # Larger font for IP

# Icon mapping for weather
icon_mapping = {
    "clear sky": "01.bmp",
    "few clouds": "02.bmp",
    "scattered clouds": "03.bmp",
    "broken clouds": "04.bmp",
    "shower rain": "09.bmp",
    "rain": "10.bmp",
    "thunderstorm": "11.bmp",
    "snow": "13.bmp",
    "mist": "50.bmp"
}

# Function to fetch weather data from OpenWeatherMap
def fetch_weather_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={config.CITY}&appid={config.API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    description = data['weather'][0]['description'].capitalize()
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    return description, temperature, humidity

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

def display_system_info():
    ip_address = get_ip_address()
    cpu_usage = get_cpu_usage()
    memory_usage_percent, memory_used, memory_total = get_memory_usage()
    temperature = get_temperature()
    disk_usage_percent, disk_used, disk_total = get_disk_usage()

    with Image.new('1', (device.width, device.height), 0) as image:
        draw = ImageDraw.Draw(image)

        # Draw IP address with larger font
        draw.text((0, 0), f"IP: {ip_address}", font=ip_font, fill="yellow")
        
        # Combine CPU and Temperature on one line
        draw.text((0, 15), f"CPU: {cpu_usage}%  Temp: {temperature}", font=default_font, fill="blue")

        # Memory Usage in GB with percentage
        draw.text((0, 30), f"RAM: {memory_used:.2f}/{memory_total:.2f}GB ({memory_usage_percent}%)", font=default_font, fill="blue")
        
        # Disk Usage in GB with percentage
        draw.text((0, 45), f"Disk: {disk_used:.2f}/{disk_total:.2f}GB ({disk_usage_percent}%)", font=default_font, fill="blue")

        device.display(image)

def display_weather_info(description, temperature, humidity):
    # Round temperature and low temperature
    rounded_temperature = math.ceil(temperature)
    rounded_low_temp = math.ceil(temperature - 5)  # Example calculation for low temperature

    # Determine the icon based on the description
    icon_file = icon_mapping.get(description.lower(), "unknown.bmp")
    icon_path = f'/home/pi/oled_project/icons/{icon_file}'

    # Load the BMP image
    icon = Image.open(icon_path).resize((32, 32), Image.Resampling.LANCZOS)

    with Image.new('1', (device.width, device.height), 0) as image:
        draw = ImageDraw.Draw(image)

        # Define fonts
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()  # Use a smaller font for time if needed

        # Add city name at the top-left corner
        city_name = f"{config.CITY.capitalize()}, {config.COUNTRY.upper()}"
        city_name_x = 0
        city_name_y = 0
        draw.text((city_name_x, city_name_y), city_name, font=font, fill=255)  # White text

        # Add current date at the top-right corner
        current_date = datetime.now().strftime("%d %b %Y")
        date_bbox = draw.textbbox((0, 0), current_date, font=font)
        date_width = date_bbox[2] - date_bbox[0]
        date_x = device.width - date_width
        date_y = 0
        draw.text((date_x, date_y), current_date, font=font, fill=255)  # White text

        # Adjust the position to move the icon to the right
        icon_x = device.width - 45  # Right side of the screen
        icon_y = 10  # Move the icon down to ensure enough space for text
        image.paste(icon, (icon_x, icon_y))  # Paste icon on the right

        # Add weather description text below the icon (2 lines if 2 words)
        description_lines = description.split(" ")  # Split description into words

        # Check if description has more than one word
        if len(description_lines) > 1:
            line1 = description_lines[0]  # First word
            line2 = " ".join(description_lines[1:])  # Remaining words
        else:
            line1 = description
            line2 = ""

        description_x = icon_x - 10  # Move text slightly to the left (reduce value)
        description_y = icon_y + 17 + 12  # Position text just below the icon

        # Draw each line of the weather description
        draw.text((description_x, description_y), line1, font=font, fill=255)  # White text
        if line2:
            draw.text((description_x, description_y + 15), line2, font=font, fill=255)  # White text

        # Add temperature and humidity on the left side
        temperature_text = f"Temp: {rounded_temperature}°C"
        low_temp_text = f"({rounded_low_temp}°C)"  # Low temperature in parentheses
        humidity_text = f"Humid: {humidity}%"

        temp_x = 0  # Start at the left side of the screen
        temp_y = 20  # Adjust vertical position from the top
        humidity_y = temp_y + 15  # Position humidity text below temperature

        # Measure text size for proper alignment
        temp_text_bbox = draw.textbbox((0, 0), temperature_text, font=font)
        temp_text_width = temp_text_bbox[2] - temp_text_bbox[0]

        # Draw temperature and low temperature beside each other
        draw.text((temp_x, temp_y), temperature_text, font=font, fill=255)  # White text
        draw.text((temp_x + temp_text_width, temp_y), low_temp_text, font=font, fill=255)  # White text
        draw.text((temp_x, humidity_y), humidity_text, font=font, fill=255)  # White text

        # Add current time at the bottom-left corner in 12-hour format with AM/PM
        current_time = datetime.now().strftime("%I:%M %p")
        time_bbox = draw.textbbox((0, 0), current_time, font=small_font)
        time_x = 0
        time_y = device.height - time_bbox[3]  # Position at the bottom of the screen
        draw.text((time_x, time_y), current_time, font=small_font, fill=255)  # White text

        device.display(image)

# Main loop to switch between pages
current_page = 1
last_weather_update = time.time()
update_interval = 60  # 1 minutes in seconds

# Initialize weather data
description, temperature, humidity = "", 0, 0

while True:
    current_time = time.time()

    if current_page == 1:
        display_system_info()
        current_page = 2
    else:
        # Update weather information every 60 seconds
        if current_time - last_weather_update > update_interval:
            description, temperature, humidity = fetch_weather_data()
            last_weather_update = current_time

        display_weather_info(description, temperature, humidity)
        current_page = 1

    time.sleep(5)  # Change pages every 5 seconds
