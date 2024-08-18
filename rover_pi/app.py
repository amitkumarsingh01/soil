import RPi.GPIO as GPIO
from flask import Flask, request, jsonify, render_template

# Pin Definitions
in1_pin = 27  # Motor 1 IN1
in2_pin = 17  # Motor 1 IN2
ena_pin = 9   # Motor 1 Enable
in3_pin = 10  # Motor 2 IN3
in4_pin = 22  # Motor 2 IN4
enb_pin = 11  # Motor 2 Enable

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(ena_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)
GPIO.setup(enb_pin, GPIO.OUT)

# Initialize PWM on Enable pins
pwm_ena = GPIO.PWM(ena_pin, 1000)  # Set frequency to 1 kHz
pwm_enb = GPIO.PWM(enb_pin, 1000)  # Set frequency to 1 kHz
pwm_ena.start(0)  # Start PWM with 0% duty cycle
pwm_enb.start(0)  # Start PWM with 0% duty cycle

app = Flask(__name__)

def set_motor_direction(left_motor_forward, right_motor_forward, speed):
    """Control both motors."""
    GPIO.output(in1_pin, GPIO.HIGH if left_motor_forward else GPIO.LOW)
    GPIO.output(in2_pin, GPIO.LOW if left_motor_forward else GPIO.HIGH)
    GPIO.output(in3_pin, GPIO.HIGH if right_motor_forward else GPIO.LOW)
    GPIO.output(in4_pin, GPIO.LOW if right_motor_forward else GPIO.HIGH)
    pwm_ena.ChangeDutyCycle(speed)
    pwm_enb.ChangeDutyCycle(speed)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forward', methods=['POST'])
def move_forward():
    set_motor_direction(True, True, 50)  # Adjust speed as needed
    return jsonify(status="Moving Forward")

@app.route('/backward', methods=['POST'])
def move_backward():
    set_motor_direction(False, False, 50)  # Adjust speed as needed
    return jsonify(status="Moving Backward")

@app.route('/left', methods=['POST'])
def turn_left():
    set_motor_direction(True, False, 50)  # Adjust speed as needed
    return jsonify(status="Turning Left")

@app.route('/right', methods=['POST'])
def turn_right():
    set_motor_direction(False, True, 50)  # Adjust speed as needed
    return jsonify(status="Turning Right")

@app.route('/stop', methods=['POST'])
def stop():
    set_motor_direction(False, False, 0)  # Stop
    return jsonify(status="Stopped")

@app.route('/increase_speed', methods=['POST'])
def increase_speed():
    current_duty = pwm_ena.duty_cycle
    new_duty = min(100, current_duty + 10)  # Increase by 10%
    pwm_ena.ChangeDutyCycle(new_duty)
    pwm_enb.ChangeDutyCycle(new_duty)
    return jsonify(status="Speed Increased", speed=new_duty)

@app.route('/decrease_speed', methods=['POST'])
def decrease_speed():
    current_duty = pwm_ena.duty_cycle
    new_duty = max(0, current_duty - 10)  # Decrease by 10%
    pwm_ena.ChangeDutyCycle(new_duty)
    pwm_enb.ChangeDutyCycle(new_duty)
    return jsonify(status="Speed Decreased", speed=new_duty)

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # Clean up GPIO and stop PWM
        set_motor_direction(False, False, 0)
        pwm_ena.stop()
        pwm_enb.stop()
        GPIO.cleanup()
