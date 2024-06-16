# led_control.py (MicroPython code for the Pico)

import network
import socket
from machine import Pin
import time

# Set up the LED
led = Pin(5, Pin.OUT)

def connect_to_wifi():
    ssid = 'your_SSID'
    password = 'your_PASSWORD'

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        time.sleep(1)

    ip_address = wlan.ifconfig()[0]
    print('Connected to Wi-Fi:', ip_address)
    return ip_address

def handle_request(request):
    request = str(request)
    if 'GET /on' in request:
        led.value(1)
        return 'HTTP/1.1 200 OK\n\nLED is ON'
    elif 'GET /off' in request:
        led.value(0)
        return 'HTTP/1.1 200 OK\n\nLED is OFF'
    else:
        return 'HTTP/1.1 404 Not Found\n\n'

def start_server(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = sock.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        response = handle_request(request)
        cl.send(response)
        cl.close()

ip_address = connect_to_wifi()
start_server(ip_address)
