import network
import socket
from machine import Pin, PWM
import time

# Define motor pins
motor1_forward = Pin(16, Pin.OUT)
motor1_backward = Pin(17, Pin.OUT)
motor2_forward = Pin(18, Pin.OUT)
motor2_backward = Pin(19, Pin.OUT)

# Define enable pins
en1 = PWM(Pin(6), freq=1000)
en2 = PWM(Pin(7), freq=1000)

# Set initial speed (60% of max speed)
initial_duty_cycle = int(0.6 * 1023)
en1.duty(initial_duty_cycle)
en2.duty(initial_duty_cycle)

def set_speed(duty):
    en1.duty(duty)
    en2.duty(duty)

def stop():
    motor1_forward.off()
    motor1_backward.off()
    motor2_forward.off()
    motor2_backward.off()

def move_forward():
    stop()
    motor1_forward.on()
    motor2_forward.on()

def move_backward():
    stop()
    motor1_backward.on()
    motor2_backward.on()

def turn_left():
    stop()
    motor1_backward.on()
    motor2_forward.on()

def turn_right():
    stop()
    motor1_forward.on()
    motor2_backward.on()

# Connect to Wi-Fi
ssid = 'Project'
password = '12345678'

def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    for _ in range(10):  # Retry up to 10 times
        if station.isconnected():
            print('Connection successful')
            print(station.ifconfig())
            return station
        print('Connecting to Wi-Fi...')
        time.sleep(1)

    raise RuntimeError('Failed to connect to Wi-Fi')

try:
    station = connect_wifi(ssid, password)
except RuntimeError as e:
    print(e)
    # Handle the Wi-Fi connection failure, e.g., by resetting the ESP32 or entering deep sleep
    raise SystemExit('Exiting due to Wi-Fi connection failure')

# Set up a web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024).decode()
    request_path = request.split(' ')[1]

    if '/forward' in request_path:
        move_forward()
    elif '/backward' in request_path:
        move_backward()
    elif '/left' in request_path:
        turn_left()
    elif '/right' in request_path:
        turn_right()
    elif '/stop' in request_path:
        stop()
    elif '/increase_speed' in request_path:
        current_duty = en1.duty()
        new_duty = min(1023, current_duty + 102)  # Increase by ~10%
        set_speed(new_duty)
    elif '/decrease_speed' in request_path:
        current_duty = en1.duty()
        new_duty = max(0, current_duty - 102)  # Decrease by ~10%
        set_speed(new_duty)

    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send('<html><body>OK</body></html>')
    cl.close()

