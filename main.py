from machine import Pin, ADC
import ujson
import network
import utime as time
import dht
import urequests as requestss
import requests

# Constants for pin and state
SENSOR_PIN = 19  # ESP32 pin connected to HC-SR501 motion sensor
DHT_PIN = 21  # DHT11 sensor pin
LDR_PIN = 33  # LDR sensor pin

dht_sensor = dht.DHT11(Pin(DHT_PIN))
HC_SR501 = Pin(SENSOR_PIN, Pin.IN)
ldr = ADC(Pin(LDR_PIN))
ldr.width(ADC.WIDTH_12BIT)  # Set ADC resolution to 12-bit
ldr.atten(ADC.ATTN_11DB)  # Set attenuation to 11 dB

# WiFi and Ubidots configuration
DEVICE_ID = "esp32-sic6"
WIFI_SSID = "Micmatthome"
WIFI_PASSWORD = "Mic2matt"
TOKEN = "BBUS-hTmr6XQtCHKNgvyTVH7wUdz08r6OUM"

# Function to create JSON data
def create_json_data(temperature, humidity, motion, light):
    data = ujson.dumps({
        "temp": temperature,
        "humidity": humidity,
        "motion": motion,
        "light": light,
    })
    return data

# Function to send data to Ubidots
def send_data(temperature, humidity, motion, light):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    apiurl = "https://whole-unique-bison.ngrok-free.app/add_data"
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    data = {
        "temp": temperature,
        "humidity": humidity,
        "motion": motion,
        "light": light,
    }
    response = requestss.post(url, json=data, headers=headers)
    responce = requests.post(apiurl, json=data)
    print("Response:", response.text)

# Connect to WiFi
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting...")
    time.sleep(0.1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

# Initialize state variables
motion_state = 0
prev_motion_state = 0

time.sleep(2)  # Delay before starting loop

# Main loop
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        temp_f = temp * (9/5) + 32.0
        light = ldr.read()

        # Determine light description based on thresholds
        if light < 41:
            light_description = "Dark"
        elif light < 819:
            light_description = "Dim"
        elif light < 2048:
            light_description = "Light"
        elif light < 3277:
            light_description = "Bright"
        else:
            light_description = "Very bright"

        print(f'Temperature: {temp:.1f} C')
        print(f'Temperature: {temp_f:.1f} F')
        print(f'Humidity: {hum:.1f} %')
        print(f'Light Intensity: {light} - {light_description}')
    except OSError:
        print('Failed to read sensor.')
        temp, hum, light, light_description = None, None, None, "Unknown"  # Set to None if reading fails
    
    prev_motion_state = motion_state  # Store previous motion state
    motion_state = HC_SR501.value()  # Read current motion sensor state

    # Check for motion detection
    if prev_motion_state == 0 and motion_state == 1:
        print("Motion detected!")
    elif prev_motion_state == 1 and motion_state == 0:
        print("Motion stopped!")

    # Send data to Ubidots
    send_data(temp, hum, motion_state, light)
    
    time.sleep(2)  # Delay to prevent spamming requests