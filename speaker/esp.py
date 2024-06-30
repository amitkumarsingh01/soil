import network
import socket
import machine
from machine import DAC

# Connect to Wi-Fi
ssid = 'home wifi-2.4G'
password = 'biharirocks'
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

# Setup DAC on GPIO25 (adjust pin as needed)
dac = DAC(machine.Pin(25))

# Function to play audio
def play_audio(audio_data):
    for i in range(0, len(audio_data), 2):
        sample = int.from_bytes(audio_data[i:i+2], 'little', signed=True)
        dac.write(sample)

# Socket client to receive audio data
def receive_audio():
    while True:
        try:
            client = socket.socket()
            server_ip = '192.168.1.19'  # Replace with your Flask server's IP address
            server_port = 5000  # Replace with the port used by your Flask server
            client.connect((server_ip, server_port))
            print('Connected to server')

            while True:
                data = client.recv(1024)
                if not data:
                    break
                play_audio(data)

            client.close()
        except Exception as e:
            print('Error:', e)

# Start receiving audio
receive_audio()

