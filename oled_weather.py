#oled_weather.py
#author : souvik roychoudhury
#version : 12
# for oled 0.96 weather station // city & country name, date & time, temperature (current & low) & humidity, whether description & icon.


import time
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import config  # Assuming your API key and city are stored in config.py
import math

# Initialize the display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Icon mapping
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

# Function to display BMP image, weather description, and additional information on OLED
def display_icon_with_description_and_data():
    # Fetch weather data
    description, temperature, humidity = fetch_weather_data()

    # Round temperature and low temperature
    rounded_temperature = math.ceil(temperature)
    rounded_low_temp = math.ceil(temperature - 5)  # Example calculation for low temperature

    # Determine the icon based on the description
    icon_file = icon_mapping.get(description.lower(), "unknown.bmp")
    icon_path = f'/home/pi/oled_project/icons/{icon_file}'

    # Load the BMP image
    icon = Image.open(icon_path).resize((32, 32), Image.Resampling.LANCZOS)

    # Create a blank image
    image = Image.new('1', (device.width, device.height), 0)  # Black background
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

    # Display the image on OLED
    device.display(image)

# Main function to run the display continuously
if __name__ == "__main__":
    try:
        while True:
            display_icon_with_description_and_data()
            time.sleep(60)  # Update every 60 seconds
    except KeyboardInterrupt:
        pass

