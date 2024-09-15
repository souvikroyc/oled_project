#oled_project
#author : souvik roychoudhury
#version : 4.0
#feature: without welcome screen || it has only IP, CPU, Temp, RAM and Disk information || with weather information

import time
import subprocess
import psutil
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw, Image
import requests
from datetime import datetime
from config import API_KEY, CITY  # Import API key and city from config file

# OLED setup
serial = i2c(port=1, address=0x3C)  # Adjust the I2C address if needed
device = ssd1306(serial, width=128, height=64)

# Load fonts
default_font = ImageFont.load_default()  # Small default font
large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)  # Larger font for weather
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)  # Medium font for IP, weather
small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)   # Small font for date/time

# Load weather icons directory
icons_path = "icons/"

# OpenWeatherMap API setup
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Function to get weather data from OpenWeatherMap
def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        temp = data['main']['temp']
        weather_desc = data['weather'][0]['description'].lower()  # Get detailed weather description in lowercase
        city = data['name']
        country = data['sys']['country']
        humidity = data['main']['humidity']
        return f"{temp}°C", weather_desc, city, country, humidity
    except Exception as e:
        return "N/A", "N/A", "N/A", "N/A", "N/A"

# Weather icon mapping dictionary
weather_icons = {
    "clear sky": "sunny.png",
    "few clouds": "cloudy.png",
    "scattered clouds": "cloudy.png",
    "broken clouds": "cloudy.png",
    "shower rain": "rain.png",
    "rain": "rain.png",
    "thunderstorm": "thunderstorm.png",
    "snow": "snow.png",
    "mist": "mist.png",
    "fog": "fog.png",
    "haze": "fog.png"
}

# Function to load the correct weather icon based on the description
def get_weather_icon(weather_desc):
    icon_file = weather_icons.get(weather_desc, "cloudy.png")  # Default to cloudy if not found
    return Image.open(icons_path + icon_file).resize((32, 32)).convert("1")

# Function to get the Raspberry Pi IP address
def get_ip_address():
    cmd = "hostname -I | cut -d' ' -f1"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

# Function to get CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get memory usage
def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / (1024 * 1024 * 1024), mem.total / (1024 * 1024 * 1024)

# Function to get the Raspberry Pi temperature
def get_temperature():
    temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
    return temp.replace("temp=", "").strip()

# Function to get disk usage
def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent, disk.used / (1024 * 1024 * 1024), disk.total / (1024 * 1024 * 1024)

# Function to get current date and time
def get_current_time():
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
    date_str = now.strftime("%d/%b/%Y")  # DD/MMM/YYYY format (e.g., 14/Sep/2024)
    return date_str, time_str

# Main loop for displaying system stats and date/time/weather
page = 0  # Page toggle (0 for system stats, 1 for date/time/weather)
while True:
    if page == 0:
        # Display system stats
        ip_address = get_ip_address()
        cpu_usage = get_cpu_usage()
        memory_usage_percent, memory_used, memory_total = get_memory_usage()
        temperature = get_temperature()
        disk_usage_percent, disk_used, disk_total = get_disk_usage()

        with canvas(device) as draw:
            # Draw IP address with medium font
            draw.text((0, 0), f"IP: {ip_address}", font=large_font, fill="yellow")
            
            # Combine CPU and Temperature on one line
            draw.text((0, 15), f"CPU: {cpu_usage}%  Temp: {temperature}", font=default_font, fill="blue")

            # Memory Usage in GB with percentage
            draw.text((0, 30), f"RAM: {memory_used:.2f}/{memory_total:.2f}GB ({memory_usage_percent}%)", font=default_font, fill="blue")
            
            # Disk Usage in GB with percentage
            draw.text((0, 45), f"Disk: {disk_used:.2f}/{disk_total:.2f}GB ({disk_usage_percent}%)", font=default_font, fill="blue")
    
    else:
        # Display date, time, and weather
        date_str, time_str = get_current_time()
        temp, weather_desc, city, country, humidity = get_weather()

        with canvas(device) as draw:
            # Display reduced-size date and time on the top line
            draw.text((0, 0), f"{date_str} {time_str}", font=medium_font, fill="yellow")

            # Display city and country below date and time
            draw.text((0, 20), f"Weather for:{city},{country}", font=default_font, fill="blue")

            # Load the appropriate weather icon
            weather_icon = get_weather_icon(weather_desc)

            # Display weather icon on the left side
            draw.bitmap((0, 35), weather_icon, fill="white")

            # Display temperature on the right side next to the icon
            draw.text((40, 35), f"{temp}, {humidity}%", font=large_font, fill="blue")  # Weather temp in large font

            # Display weather description on the right side, below the temperature
            # Ensure text fits within the screen by using multiple lines if needed
            lines = [weather_desc.capitalize()[:16], weather_desc.capitalize()[16:32]]
            for i, line in enumerate(lines):
                draw.text((40, 50 + i * 10), line, font=default_font, fill="blue")

            # Display humidity below the weather description
            draw.text((0, 50 + len(lines) * 10), f"Humidity: {humidity}%", font=default_font, fill="blue")

    # Toggle pages every 5 seconds
    page = (page + 1) % 2
    time.sleep(5)
