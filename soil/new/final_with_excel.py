import machine
import uasyncio as asyncio
import network
import json
import utime

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
sensor_pins = [machine.ADC(28), machine.ADC(27), machine.ADC(26)] 

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
    <br>
    <br>
    <br>
    <table id="sensorTable">
        <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Sensor 1</th>
            <th>Sensor 2</th>
            <th>Sensor 3</th>
            <th>Average</th>
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
                const sensor2Cell = row.insertCell(3);
                const sensor3Cell = row.insertCell(4);
                const averageCell = row.insertCell(5);
                
                const now = new Date();
                const date = now.toLocaleDateString();
                const time = now.toLocaleTimeString();
                
                dateCell.textContent = date;
                timeCell.textContent = time;
                sensor1Cell.textContent = data.sensor1.toFixed(2) + '%';
                sensor2Cell.textContent = data.sensor2.toFixed(2) + '%';
                sensor3Cell.textContent = data.sensor3.toFixed(2) + '%';
                averageCell.textContent = data.average.toFixed(2) + '%';
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

    # Read the rest of the request headers
    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break

    if request_line.startswith(b"GET /data"):
        sensor_data = read_sensors()
        avg_value = sum(sensor_data) / len(sensor_data)

        response_data = {
            "sensor1": sensor_data[0],
            "sensor2": sensor_data[1],
            "sensor3": sensor_data[2],
            "average": avg_value
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
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Server running on http://0.0.0.0:80")
    
    while True:
        await asyncio.sleep(3600)  # Keep the server running indefinitely

asyncio.run(main())


