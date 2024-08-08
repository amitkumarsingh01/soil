import uasyncio as asyncio
import network
import json
import utime
from machine import UART, Pin, PWM, ADC
from ibus import IBus
from servo import Servo
from motor_driver import MotorDriver
from linearact import LinearActuator

# Network setup (from soil.py)
ssid = 'Project'
password = '12345678'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    print("Connecting to network...")
    utime.sleep(1)

print("Network connected:", wlan.ifconfig())

# Sensor setup (from soil.py)
sensor_pins = [ADC(28)]

def read_sensors():
    values = [sensor.read_u16() for sensor in sensor_pins]
    percentages = [100 - (value / 65535 * 100) for value in values]  # Calculate percentage
    return percentages

html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sensor Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            background-color: #000;
            color: #FFD700;
        }
        h1 {
            color: #FFD700;
            margin-bottom: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
        }
        th, td {
            border: 1px solid #FFD700;
            padding: 10px;
        }
        th {
            background-color: #333;
            color: #FFD700;
        }
        td {
            background-color: #444;
            color: #FFD700;
        }
    </style>
</head>
<body>
    <h1>Sensor Data</h1>
    <table id="sensorTable">
        <tr>
            <th>Timestamp</th>
            <th>Sensor 1</th>
        </tr>
    </table>

    <script>
        async function fetchData() {
            try {
                const response = await fetch("/data");
                const data = await response.json();
                
                const table = document.getElementById('sensorTable');
                const row = table.insertRow();
                const timestampCell = row.insertCell(0);
                const sensor1Cell = row.insertCell(1);
                
                const timestamp = new Date().toLocaleString();
                timestampCell.textContent = timestamp;
                sensor1Cell.textContent = data.sensor1.toFixed(2) + '%';
            } catch (error) {
                console.error('Error fetching sensor data:', error);
            }
        }

        setInterval(fetchData, 1000);
        fetchData();
    </script>
</body>
</html>
"""
async def handle_client(reader, writer):
    request_line = await reader.readline()
    print("Request:", request_line)

    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break

    if request_line.startswith(b"GET /data"):
        sensor_data = read_sensors()
        avg_value = sum(sensor_data) / len(sensor_data)

        response_data = {
            "sensor1": sensor_data[0],
        }

        response = json.dumps(response_data)
        writer.write('HTTP/1.1 200 OK\r\n')
        writer.write('Content-Type: application/json\r\n')
        writer.write('Connection: close\r\n')
        writer.write('\r\n')
        writer.write(response)
    else:
        writer.write('HTTP/1.1 200 OK\r\n')
        writer.write('Content-Type: text/html\r\n')
        writer.write('Connection: close\r\n')
        writer.write('\r\n')
        writer.write(html)

    await writer.drain()
    await writer.aclose()

# Initialize motor drivers, servos, linear actuators, etc. (from main.py)
motor_driver1 = MotorDriver(pin1=12, pin2=13, pin3=14, pin4=15)
motor_driver2 = MotorDriver(pin1=0, pin2=1, pin3=2, pin4=3)
servo_pins = [16, 17, 18, 19, 20, 21]
servos = [Servo(pin) for pin in servo_pins]
ibus_in = IBus(1)
linear_actuator = LinearActuator(pin1=8, pin2=9)

def servo_Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_servo_angle(pin, angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180
    servo_index = servo_pins.index(pin)
    servos[servo_index].goto(round(servo_Map(angle, 0, 180, 0, 1024)))

def servo_control(channel_value):
    # (Your servo control logic from main.py)

async def ibus_main():
    while True:
        res = ibus_in.read()
        if res[0] == 1:
            ch1_normalized = IBus.normalize(res[1])
            ch2_normalized = IBus.normalize(res[2])
            ch3_normalized = IBus.normalize(res[3])
            ch4_normalized = IBus.normalize(res[4])
            ch5_normalized = IBus.normalize(res[5], type="dial")
            ch6_normalized = IBus.normalize(res[6], type="dial")

            print("Status {} CH 1 {} CH 2 {} CH 3 {} CH 4 {} CH 5 {} CH 6 {}".format(
                res[0],
                ch1_normalized,
                ch2_normalized,
                ch3_normalized,
                ch4_normalized,
                ch5_normalized,
                ch6_normalized),
                end="")
            print(" - {}".format(time.ticks_ms()))

            motor_speed = int(ch2_normalized)
            motor_driver1.set_speed(motor_speed)
            motor_driver2.set_speed(motor_speed)

            # Control servos and linear actuator
            servo_control(ch4_normalized)
            linear_actuator.control(ch5_normalized)

            await asyncio.sleep(0.1)
        else:
            print("Status offline {}".format(res[0]))
            await asyncio.sleep(0.1)

async def main():
    # Run both the server and the ibus_main function concurrently
    server_task = asyncio.start_server(handle_client, "0.0.0.0", 80)
    ibus_task = ibus_main()

    await asyncio.gather(server_task, ibus_task)

# Run the asyncio loop
asyncio.run(main())
