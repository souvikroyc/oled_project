# oled_stats.py

import time
import requests
import subprocess
import psutil
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw, Image
from config import API_KEY, CITY, WEATHER_URL, icons_path  # Importing from config

# OLED setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=64)

# Load fonts
default_font = ImageFont.load_default()
large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
weather_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # Adjust size as needed

# Weather icon mapping dictionary
def get_weather_icon(weather_desc):
    # Check if any known weather type is a substring of the description
    if "clear" in weather_desc:
        icon_file = "sunny.png"
    elif "cloud" in weather_desc:
        icon_file = "cloudy.png"
    elif "rain" in weather_desc or "drizzle" in weather_desc:
        icon_file = "rain.png"
    elif "thunderstorm" in weather_desc:
        icon_file = "thunderstorm.png"
    elif "snow" in weather_desc:
        icon_file = "snow.png"
    elif "mist" in weather_desc or "fog" in weather_desc or "haze" in weather_desc:
        icon_file = "fog.png"
    elif "smoke" in weather_desc:
        icon_file = "smoke.png"
    elif "dust" in weather_desc:
        icon_file = "dust.png"
    elif "sand" in weather_desc:
        icon_file = "sandstorm.png"
    elif "tornado" in weather_desc:
        icon_file = "tornado.png"
    elif "ash" in weather_desc:
        icon_file = "ash.png"
    elif "squall" in weather_desc:
        icon_file = "squall.png"
    else:
        icon_file = "cloudy.png"  # Default to cloudy if not found
    
    # Load and return the icon image
    return Image.open(icons_path + icon_file).resize((32, 32)).convert("1")

# Function to fetch weather data
def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        temp = data['main']['temp']
        weather_desc = data['weather'][0]['main'].lower()  # Get weather condition in lowercase
        return f"{temp}°C", weather_desc
    except Exception as e:
        return "N/A", "N/A"

# Main loop for displaying system stats and weather
while True:
    temp, weather_desc = get_weather()

    with canvas(device) as draw:
        # Draw weather information
        weather_icon = get_weather_icon(weather_desc)
        draw.bitmap((0, 0), weather_icon, fill="white")
        draw.text((40, 0), f"{temp}", font=weather_font, fill="white")

    time.sleep(60)  # Update every minute
