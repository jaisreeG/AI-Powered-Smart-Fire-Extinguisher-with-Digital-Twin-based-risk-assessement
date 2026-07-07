import serial
import time
import pickle
import pandas as pd
from twilio.rest import Client as TwilioClient
from Adafruit_IO import Client as AdafruitIOClient
from flask_server import update_risk

# Adafruit IO (Replace with your credentials)
ADAFRUIT_USERNAME = "your_username"
ADAFRUIT_KEY = "your_adafruit_key"
aio = AdafruitIOClient(ADAFRUIT_USERNAME, ADAFRUIT_KEY)
group_prefix = "smart-fire-safety-network."

# Twilio (Replace with your credentials)
TWILIO_SID = 'your_twilio_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_NUMBER = '+1xxxxxxxxxx'
MY_PHONE_NUMBER = '+91xxxxxxxxxx'

twilio_client = TwilioClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms(msg):
    try:
        twilio_client.messages.create(body=msg, from_=TWILIO_NUMBER, to=MY_PHONE_NUMBER)
        print("📱 SMS Sent")
    except Exception as e:
        print("SMS Error:", e)

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print("Model Load Error:", e)
    exit()

try:
    arduino = serial.Serial('COM9', 115200, timeout=1)
    time.sleep(2)
except Exception as e:
    print("Arduino Error:", e)
    exit()

prev_data = None
sms_sent = False
update_counter = 0
UPDATE_INTERVAL = 20
last_send_time = time.time()

while True:
    try:
        while arduino.in_waiting > 0:
            line = arduino.readline().decode().strip()
            print(f"Raw Arduino: {line}")

            parts = line.split(',')
            if len(parts) >= 5:
                temp, humidity, smoke, flame, tempspike = map(float, parts[:5])
                input_df = pd.DataFrame([[temp, humidity, smoke, int(flame), int(tempspike)]],
                                        columns=["temperature", "humidity", "smoke", "flame", "tempspike"])
                prediction = int(model.predict(input_df)[0])
                update_counter += 1

                if update_counter >= UPDATE_INTERVAL or (temp, humidity, smoke, flame, prediction) != prev_data:
                    print(f" AI ➜ Temp: {temp}°C | Humidity: {humidity}% | Smoke: {smoke} | Flame: {flame} | Risk: {prediction}")
                    update_risk(prediction)

                    if time.time() - last_send_time >= 2:
                        aio.send(group_prefix + 'temperature', temp)
                        aio.send(group_prefix + 'humidity', humidity)
                        aio.send(group_prefix + 'smoke', smoke)
                        aio.send(group_prefix + 'flame', flame)
                        aio.send(group_prefix + 'firerisk', prediction)
                        last_send_time = time.time()

                    if prediction == 1 and not sms_sent:
                        send_sms(f"Fire Detected!\nTemp: {temp}°C\nSmoke: {smoke}\nFlame: {flame}")
                        sms_sent = True
                    elif prediction == 0:
                        sms_sent = False

                    prev_data = (temp, humidity, smoke, flame, prediction)
                    update_counter = 0

        time.sleep(0.1)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print("Runtime Error:", e)
        break
