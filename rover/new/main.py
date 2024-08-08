import utime
import machine
import uasyncio as asyncio
import network
import json
from ibus import IBus
from motor_driver import MotorDriver
from linearact import LinearActuator  # Import the LinearActuator class
from machine import Pin, PWM, ADC
from servo import Servo

# Initialize motor drivers
motor_driver1 = MotorDriver(pin1=12, pin2=13, pin3=14, pin4=15)
motor_driver2 = MotorDriver(pin1=0, pin2=1, pin3=2, pin4=3)

# Initialize servos connected to pins 16, 17, 18, 19, 20, and 21
servo_pins = [16, 17, 18, 19, 20, 21]
servos = [Servo(pin) for pin in servo_pins]

ibus_in = IBus(1)  # UART1

# Initialize linear actuator connected to pins 8 and 9
linear_actuator = LinearActuator(pin1=8, pin2=9)

# Define the GPIO pins connected to the sensors
sensor_pins = [ADC(28)] 

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
    if -100 <= channel_value <= -70:
        set_servo_angle(16, 37)
        set_servo_angle(17, 45)
        set_servo_angle(20, 90)
        set_servo_angle(21, 90)
        set_servo_angle(18, 135)
        set_servo_angle(19, 130)
    elif -30 < channel_value < 30:
        set_servo_angle(16, 82)
        set_servo_angle(17, 90)
        set_servo_angle(18, 90)
        set_servo_angle(19, 85)
        set_servo_angle(20, 90)
        set_servo_angle(21, 90)
    elif 70 <= channel_value <= 100:
        set_servo_angle(16, 127)
        set_servo_angle(17, 135)
        set_servo_angle(18, 45)
        set_servo_angle(19, 40)
        set_servo_angle(20, 90)
        set_servo_angle(21, 90)

def read_sensors():
    values = [sensor.read_u16() for sensor in sensor_pins]
    percentages = [100 - (value / 65535 * 100) for value in values]  # Calculate percentage
    return percentages

# HTML content to serve to the client
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
        #downloadButton {
            padding: 10px 20px;
            background-color: #FFD700;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Sensor Data</h1>
    
    <button id="downloadButton" onclick="downloadCSV()">Download Data</button>
    <br><br><br>
    <table id="sensorTable">
        <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Sensor</th>
        </tr>
    </table>

    <script>
        async function fetchData() {
            try {
                const response = await fetch("/data");
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                
                const table = document.getElementById('sensorTable');
                const row = table.insertRow();
                const dateCell = row.insertCell(0);
                const timeCell = row.insertCell(1);
                const sensor1Cell = row.insertCell(2);
                
                const now = new Date();
                const date = now.toLocaleDateString();
                const time = now.toLocaleTimeString();
                
                dateCell.textContent = date;
                timeCell.textContent = time;
                sensor1Cell.textContent = data.sensor1.toFixed(2) + '%';
            } catch (error) {
                console.error('Error fetching sensor data:', error);
            }
        }

        function downloadCSV() {
            const table = document.getElementById('sensorTable');
            let csvContent = '';
            
            for (let row of table.rows) {
                let rowData = [];
                for (let cell of row.cells) {
                    rowData.push(cell.textContent);
                }
                csvContent += rowData.join(',') + '\\n';
            }
            
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', 'sensor_data.csv');
            document.body.appendChild(a);  // Required for Firefox
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        setInterval(fetchData, 1000);
        fetchData();
    </script>
</body>
</html>
"""

async def handle_client(reader, writer):
    request_line = await reader.readline()
    print("Request:", request_line.decode())

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
        writer.write(b'HTTP/1.1 200 OK\r\n')
        writer.write(b'Content-Type: application/json\r\n')
        writer.write(b'Connection: close\r\n')
        writer.write(b'\r\n')
        writer.write(response.encode())
    else:
        writer.write(b'HTTP/1.1 200 OK\r\n')
        writer.write(b'Content-Type: text/html\r\n')
        writer.write(b'Connection: close\r\n')
        writer.write(b'\r\n')
        writer.write(html.encode())

    await writer.drain()
    await writer.aclose()

async def main():
    ssid = 'Project'
    password = '12345678'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        print("Connecting to network...")
        utime.sleep(1)

    print("Network connected:", wlan.ifconfig())
    print("IP address: ", wlan.ifconfig()[0])

    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Server running on http://0.0.0.0:80")
    
    while True:
        res = ibus_in.read()
        if res[0] == 1:
            ch1_normalized = IBus.normalize(res[1])
            ch2_normalized = IBus.normalize(res[2])
            ch3_normalized = IBus.normalize(res[3])
            ch4_normalized = IBus.normalize(res[4])
            ch5_normalized = IBus.normalize(res[5], type="dial")
            ch6_normalized = IBus.normalize(res[6], type="dial")

            motor_speed = int(ch2_normalized)
            motor_driver1.set_speed(motor_speed)
            motor_driver2.set_speed(motor_speed)

            servo_control(ch4_normalized)
            linear_actuator.control(ch5_normalized)

            await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(0.1)

asyncio.run(main())

