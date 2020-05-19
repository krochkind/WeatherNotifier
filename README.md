# WeatherNotifier

This script gets the weather forcast for the next 24 hours and sends a text
message when
1. the temperature less than a specified temperature
2. the wind is greater than a specfied speed
3. the forecast calls for rain

The script uses Gmail to send text messages as email, so it requires a Gmail
account

It uses the free 'One Call API' from openweathermap.org
    (https://openweathermap.org/api/one-call-api)

Use the *config.json* file to set your configuration settings
* openweathermap_api_key: Your API key
* latitide / longitude: Floating point GPS coordinates
* temperature_units: Fahrenheit / Celsius
* alert_thressholds: Settings to trigger email notifications
  * wind_speed: Minimum MPH before an email is sent
  * temperature: Maximum temperature before an email is sent
  * rain: True / False - Do you want to notify based on rain forecast?
* gmail_login: The Gmail login to send text messages
* gmail_pwd: The password of the Gmail account
* send_alerts_to: Array of phone numbers that get text messages
  * phone_number: Phone number that receives the text
  * wireless_carrier: The service carrier that the phone number uses (must match the *sms.json* dictionary)
