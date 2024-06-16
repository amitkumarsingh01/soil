import machine
import utime
import urequests
import network

# Connect to WiFi
ssid = 'Project'
password = '12345678'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    print("Connecting to network...")
    utime.sleep(1)

print("Network connected:", wlan.ifconfig())

# Define the GPIO pins connected to the sensors
sensor_pins = [machine.ADC(28), machine.ADC(27), machine.ADC(26)]  # Example GPIO pins

# Define your server URL
url = "http://192.168.156.176:5000/"

def read_sensors():
    values = [sensor.read_u16() for sensor in sensor_pins]
    values = [100 - (value / 65535 * 100) for value in values]  # Calculate percentage
    return values

def send_data(data):
    try:
        response = urequests.post(url, json=data)
        print(response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)

while True:
    sensor_data = read_sensors()
    
    print("Sensor Data:", sensor_data)
    data_to_send = {
        "soil_moisture1": sensor_data[0],
        "soil_moisture2": sensor_data[1],
        "soil_moisture3": sensor_data[2]
    }
    send_data(data_to_send)
    utime.sleep(10)  # Send data every 10 seconds

