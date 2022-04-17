#!/usr/bin/env python
import math
import time
import json
import csv
import grovepi
import smtplib
import os
from dotenv import load_dotenv
from grove_rgb_lcd import *
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from TemperatureDB import TemperatureReadings

# Load environment variables
load_dotenv()

# File settings
PATH = './'
FILE_NAME = 'Temperature'

# Temperature and humidity sensor settings
TEMPERATURE_SENSOR = 7
BLUE = 0
WHITE = 1

# Light sensor settings
THRESHOLD = 50 # Turn on LED once sensor exceeds threshold resistance
LIGHT_SENSOR = 1 # Grove Light Sensor to analog port
RED_LED = 3 # Port D3
GREEN_LED = 4 # Port D1
BLUE_LED = 2 # Port D2

grovepi.pinMode(LIGHT_SENSOR,"INPUT")
grovepi.pinMode(BLUE_LED,"OUTPUT")
grovepi.pinMode(GREEN_LED,"OUTPUT")
grovepi.pinMode(RED_LED,"OUTPUT")

# Email Settings
GMAIL_USER = os.getenv("")
GMAIL_PASSWORD = os.getenv("")
SEND_TO = 'test@example.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Database Settings
DB_USERNAME = os.getenv("db_username")
DB_PASSWORD = os.getenv("db_password")

def toggle_led(led, value):
    grovepi.digitalWrite(led, value)

def write_to_JSON_file(path, filename, data):
    filePathNameWithExt = './' + path + filename + '.json'
    with open(filePathNameWithExt, 'w') as fp:
        json.dump(data, fp, indent=4)

def create_CSV_file(path, filename, data):
    filePathNameWithExt = path + filename + '.csv'
    with open(filePathNameWithExt, 'w') as file:
        csv_writer = csv.writer(file)
        header =  data[0].keys()
        csv_writer.writerow(header)
        for read in data:
            csv_writer.writerow(read.values())
    file.close()

def celcius_to_fahrenheit(temperature):
    temp = (temperature * 1.8) + 32
    return temp

def sleep(seconds):
    time.sleep(seconds)

def minutes_to_seconds(minutes):
    seconds = minutes * 60
    return seconds

def operating_hours(lightSensor, threshold):
    sensorValue = grovepi.analogRead(lightSensor)
    if sensorValue <= 0:
        resistance = 0
    else:
        resistance = (float)(1023 - sensorValue) * 10 / sensorValue

    if resistance < threshold:
        return True
    else:
        return False

def reset_leds(greenLed, blueLed, redLed):
    toggle_led(greenLed, 0)
    toggle_led(blueLed, 0)
    toggle_led(redLed, 0)

def timestamp():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")

outputData = {}
outputData['Weather'] = []
temperature_readings = TemperatureReadings(DB_USERNAME, DB_PASSWORD)
i = 1

while operating_hours(LIGHT_SENSOR, THRESHOLD):
    try:
        # Get temperature and humidity from sensor     
        [tempCelcius,humidity] = grovepi.dht(TEMPERATURE_SENSOR,BLUE) 
        tempFahrenheit = celcius_to_fahrenheit(tempCelcius)

        if math.isnan(tempFahrenheit) is True or math.isnan(humidity) is True:
            raise TypeError(': nan error') 

        reset_leds(GREEN_LED, BLUE_LED, RED_LED)
        if tempFahrenheit > 60 and tempFahrenheit < 85 and humidity < 80:
            toggle_led(GREEN_LED, 1)
        elif tempFahrenheit > 85 and tempFahrenheit < 95 and humidity < 80:
            toggle_led(BLUE_LED, 1)
        elif tempFahrenheit > 95:
            toggle_led(RED_LED, 1)
        elif humidity > 80:
            toggle_led(BLUE_LED, 1)
            toggle_led(GREEN_LED, 1)

        outputData['Weather'].append({'#':i, 'Timestamp': timestamp(), 'temperature':tempFahrenheit, 'humidity':humidity})
        
        sleep(minutes_to_seconds(5))
        setRGB(0, 255, 0)
        setText("Temp: %.02f F\n Humidity: %.02f%%"%(tempFahrenheit, humidity))

        # create json file
        write_to_JSON_file(PATH, FILE_NAME, outputData)
        temperature_readings.insert_temperatures(timestamp(), tempFahrenheit, humidity)
        i += 1

    except (IOError, TypeError) as e:
        print("Error: " + str(e))  
        
reset_leds(GREEN_LED, BLUE_LED, RED_LED)

# Compose email
msg = MIMEMultipart()
msg['From'] = GMAIL_USER
msg['To'] = COMMASPACE.join([SEND_TO])
msg['Subject'] = 'Weather Report ' , timestamp()
body = 'See attached csv for the latest weather report.'

# Create CSV file
with open('outputData.json') as json_file:
    data = json.load(json_file)               
weather_data = data['Weather']
create_CSV_file(PATH, FILE_NAME, weather_data)

# Create email attachment and add to email
part = MIMEBase('application', "octet-stream")
part.set_payload(open(PATH + FILE_NAME + '.csv', "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment', filename=PATH + FILE_NAME + '.csv')
msg.attach(part)
msg.attach(MIMEText(body))

#Initiate Gmail server and send email
smtpObj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login(GMAIL_USER, GMAIL_PASSWORD)
smtpObj.sendmail(GMAIL_USER, SEND_TO, msg.as_string())
smtpObj.quit()