import network
import urequests
import utime
from machine import ADC, Pin

# WiFi credentials
SSID = 'Project'
PASSWORD = '12345678'

# ThingSpeak credentials
THINGSPEAK_API_KEY = 'your_THINGSPEAK_API_KEY'
THINGSPEAK_URL = 'http://api.thingspeak.com/update'

# Soil moisture sensor pin
SOIL_PIN = 28

adc = ADC(Pin(SOIL_PIN))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Connected to WiFi:', wlan.ifconfig())

def read_soil_moisture():
    # Read the ADC value (0-65535)
    adc_value = adc.read_u16()
    # Normalize the ADC value to percentage (0-100%)
    moisture_percentage = (adc_value / 65535) * 100
    return moisture_percentage

def send_to_thingspeak(moisture):
    payload = {'api_key': THINGSPEAK_API_KEY, 'field1': moisture}
    try:
        response = urequests.post(THINGSPEAK_URL, json=payload)
        response.close()
        print('Data sent to ThingSpeak:', payload)
    except Exception as e:
        print('Failed to send data:', e)

def main():
    connect_wifi()
    while True:
        moisture = read_soil_moisture()
        send_to_thingspeak(moisture)
        utime.sleep(15)  
if __name__ == '__main__':
    main()
