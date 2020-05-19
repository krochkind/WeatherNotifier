"""
Weather Notification

This script gets the weather forcast for the next 24 hours and sends a text
message when
   a) the temperature less than a specified temperature
   b) the wind is greater than a specfied speed
   c) the forecast calls for rain

The script uses Gmail to send text messages as email, so it requires a Gmail
account

It uses the free 'One Call API' from openweathermap.org
    (https://openweathermap.org/api/one-call-api)

Use the config.json file to set your configuration settings
    openweathermap_api_key: Your API key
    latitide / longitude: Floating point GPS coordinates
    temperature_units: Fahrenheit / Celsius
    alert_thressholds: Settings to trigger email notifications
        wind_speed: Minimum MPH before an email is sent
        temperature: Maximum temperature before an email is sent
        rain: True / False - Do you want to notify based on rain forecast?
    gmail_login: The Gmail login to send text messages
    gmail_pwd: The password of the Gmail account
    send_alerts_to: Array of phone numbers that get text messages
        phone_number: Phone number that receives the text
        wireless_carrier: The service carrier that the phone number uses
            must match the sms.json dictionary
"""

from email.message import EmailMessage
import json
import requests
import smtplib
from time import strftime, localtime

friendly_time = lambda dt : strftime("%a, %b %d %#I:%M %p", (localtime(dt)))

class WeatherItems:
    """Class to determine how to process weather data"""
    too_cold = False
    too_windy = False
    rain = False
    weather_report = ''

    def __init__(self, time_ticks, temperature, wind_speed, weather_code):
        alert_thressholds = load_json('config.json')['alert_thressholds']
        weather_codes = load_json('weather_codes.json')
        weather_codes = {int(k):str(v) for k,v in weather_codes.items()}
        self.time_ticks = time_ticks
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.__weather_code = weather_code
        self.too_cold = self.temperature <= alert_thressholds['temperature']
        self.too_windy = self.wind_speed >= alert_thressholds['wind_speed']
        self.rain = alert_thressholds['rain'] and self.__weather_code in range(200, 600)
        self.weather_report = weather_codes[self.__weather_code].title() if self.rain else ''

weather_report_item = {
    'min_temperature': {'value': float('inf'), 'time': 0},
    'max_wind':  {'value': float('-inf' ), 'time': 0},
    'rain': {'value': 'Rain', 'time': 0}
}

def load_json(file_name):
    """Load a json file from the root in to an object"""
    try:
        with open(file_name) as content:
            return json.load(content)
    except Exception:
        print(Exception)
        return {}

def create_alert_body(weather_report_item, config):
    """Create the text of the weather alert"""
    alert_text = ''
    if (weather_report_item['min_temperature']['time'] > 0):
        alert_text += f"Cold Alert: {str(weather_report_item['min_temperature']['value'])} degrees at {friendly_time(weather_report_item['min_temperature']['time'])}\n"
    if (weather_report_item['max_wind']['time'] > 0):
        alert_text += f"Wind Alert: {str(weather_report_item['max_wind']['value'])} mph at {friendly_time(weather_report_item['max_wind']['time'])}\n"
    if (weather_report_item['rain']['time'] > 0):
        alert_text += f"{weather_report_item['rain']['value']}: {friendly_time(weather_report_item['rain']['time'])}"
    send_text(alert_text, config)

def send_text(message, config):
    """Email the weather alert as a text message"""
    sms_codes = load_json('sms.json')

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = 'Weather Alert'
    msg['From'] = config['gmail_login']

    for notify in config['send_alerts_to']:
        msg['To'] = notify['phone_number'] + "@" + sms_codes[notify['wireless_carrier']]

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(config['gmail_login'], config['gmail_pwd'])
            server.send_message(msg)
            server.quit()
        except Exception:
            print(Exception)
        else:
            print("Message sent to " + msg['To'])
            print(message)

def main():
    config = load_json('config.json')

    api_key = config['openweathermap_api_key']
    lat = config['latitide']
    lon = config['longitude']
    units = ('Imperial'
             if config['temperature_units'].lower() == 'fahrenheit'
             else 'Metric')
    api_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units={units}&exclude=minutely&appid={api_key}"
    
    response = requests.get(api_url)
    weather_data = response.content.decode("utf-8")
    weather_dict = json.loads(weather_data)

    hourly = weather_dict["hourly"]
    for h in hourly:
        time_ticks = h['dt']
        temperature = h['temp']
        wind_speed =  h['wind_speed']
        weather_code = h['weather'][0]['id']

        weather_item = WeatherItems(time_ticks, temperature, wind_speed, 
                                    weather_code)

        if (weather_item.too_cold):
            if (weather_report_item['min_temperature']['time'] == 0):
                weather_report_item['min_temperature']['value'] = weather_item.temperature
                weather_report_item['min_temperature']['time'] = weather_item.time_ticks
        
        if (weather_item.too_windy):
            if (weather_report_item['max_wind']['time'] == 0):
                weather_report_item['max_wind']['value'] = weather_item.wind_speed
                weather_report_item['max_wind']['time'] = weather_item.time_ticks

        # Return first instance of rain or weather event with the most rain?
        if (weather_item.rain):
            if (weather_report_item['rain']['time'] == 0):
                weather_report_item['rain']['value'] = weather_item.weather_report
                weather_report_item['rain']['time'] = weather_item.time_ticks

    if (weather_report_item['min_temperature']['time'] > 0 or
        weather_report_item['max_wind']['time'] > 0 or
        weather_report_item['rain']['time'] > 0):
            create_alert_body(weather_report_item, config)

if __name__ == "__main__":
    main()