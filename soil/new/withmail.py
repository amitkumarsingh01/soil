import machine
import uasyncio as asyncio
import network
import json
import utime
import umail

# Email setup
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_sender = 'aksmlibts@gmail.com'
email_password = 'obzbhhkluaivnziu'
email_recipient = 'aksdsce@gmail.com'

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

def read_sensors():
    values = [sensor.read_u16() for sensor in sensor_pins]
    values = [100 - (value / 65535 * 100) for value in values]  # Calculate percentage
    return values

async def send_email(sensor_data):
    smtp = umail.SMTP(smtp_server, smtp_port)
    smtp.login(email_sender, email_password)
    smtp.to(email_recipient)
    smtp.write("From: {}\n".format(email_sender))
    smtp.write("To: {}\n".format(email_recipient))
    smtp.write("Subject: Sensor Alert\n")
    smtp.write("\n")
    smtp.write("Sensor values are below 40%:\n")
    for i, value in enumerate(sensor_data):
        smtp.write("Sensor {}: {:.2f}%\n".format(i+1, value))
    smtp.send()
    smtp.quit()

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
        .sensor {
            margin: 20px;
            font-size: 1.5em;
        }
        .average {
            margin: 20px;
            font-size: 2em;
            font-weight: bold;
        }
        .card {
            background-color: #333;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }
    </style>
</head>
<body>
    <h1>Sensor Data</h1>
    <div class="card sensor" id="sensor1">Sensor 1: <span id="value1">Loading...</span></div>
    <div class="card sensor" id="sensor2">Sensor 2: <span id="value2">Loading...</span></div>
    <div class="card sensor" id="sensor3">Sensor 3: <span id="value3">Loading...</span></div>
    <div class="card average" id="average">Average: <span id="avg_value">Loading...</span></div>

    <script>
        async function fetchData() {
            try {
                const response = await fetch("/data");
                const data = await response.json();
                document.getElementById('value1').textContent = data.sensor1.toFixed(2) + '%';
                document.getElementById('value2').textContent = data.sensor2.toFixed(2) + '%';
                document.getElementById('value3').textContent = data.sensor3.toFixed(2) + '%';
                document.getElementById('avg_value').textContent = data.average.toFixed(2) + '%';
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

    # Read the rest of the request headers
    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break

    if request_line.startswith(b"GET /data"):
        sensor_data = read_sensors()
        avg_value = sum(sensor_data) / len(sensor_data)

        # Check if any sensor value is below 40% and send email
        if any(value < 40 for value in sensor_data):
            await send_email(sensor_data)

        response_data = {
            "sensor1": sensor_data[0],
            "sensor2": sensor_data[1],
            "sensor3": sensor_data[2],
            "average": avg_value
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

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    await server.wait_closed()

asyncio.run(main())

