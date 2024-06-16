import utime
from ibus import IBus
from servo import Servo
import time
from machine import UART, Pin, PWM
from ibus import IBus
from motor_driver import MotorDriver
from linearact import LinearActuator  # Import the LinearActuator class

# Initialize motor drivers
motor_driver1 = MotorDriver(pin1=12, pin2=13, pin3=14, pin4=15)
motor_driver2 = MotorDriver(pin1=0, pin2=1, pin3=2, pin4=3)

# Initialize servos connected to pins 16, 17, 18, 19, 20, and 21
servo_pins = [16, 17, 18, 19, 20, 21]
servos = [Servo(pin) for pin in servo_pins]

ibus_in = IBus(1)  # UART1

# Initialize linear actuator connected to pins 8 and 9
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
    # Map channel value to servo angles
    if -100 <= channel_value <= -70:
        set_servo_angle(16, 37)
        set_servo_angle(17, 45)
        set_servo_angle(18, 90)
        set_servo_angle(19, 90)
        set_servo_angle(20, 135)
        set_servo_angle(21, 130)
    elif -70 <= channel_value <= -30:
        set_servo_angle(16, 52)
        set_servo_angle(17, 60)
        set_servo_angle(18, 90)
        set_servo_angle(19, 90)
        set_servo_angle(20, 120)
        set_servo_angle(21, 115)
    elif -30 < channel_value < 30:
        set_servo_angle(16, 82)
        set_servo_angle(17, 90)
        set_servo_angle(18, 90)
        set_servo_angle(19, 90)
        set_servo_angle(20, 90)
        set_servo_angle(21, 85)
    elif 30 <= channel_value <= 70:
        set_servo_angle(16, 112)
        set_servo_angle(17, 120)
        set_servo_angle(18, 90)
        set_servo_angle(19, 90)
        set_servo_angle(20, 60)
        set_servo_angle(21, 55)
    elif 70 <= channel_value <= 100:
        set_servo_angle(16, 127)
        set_servo_angle(17, 135)
        set_servo_angle(18, 90)
        set_servo_angle(19, 90)
        set_servo_angle(20, 45)
        set_servo_angle(21, 40)

if __name__ == '__main__':
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

            # Control servos based on Channel 4 input
            servo_control(ch4_normalized)

            # Control linear actuator based on Channel 5 input
            linear_actuator.control(ch5_normalized)

            # Sleep to prevent rapid loop execution
            utime.sleep(0.1)
        else:
            print("Status offline {}".format(res[0]))
            utime.sleep(0.1)
