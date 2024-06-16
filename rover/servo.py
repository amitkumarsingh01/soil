from machine import Pin, PWM

class Servo:
    def __init__(self, pin: int or Pin or PWM, minVal=2500, maxVal=7500):

        if isinstance(pin, int):
            pin = Pin(pin, Pin.OUT)
        if isinstance(pin, Pin):
            self.__pwm = PWM(pin)
        if isinstance(pin, PWM):
            self.__pwm = pin
        self.__pwm.freq(50)
        self.minVal = minVal
        self.maxVal = maxVal

    def deinit(self):
        self.__pwm.deinit()

    def goto(self, value: int):
        if value < 0:
            value = 0
        if value > 1024:
            value = 1024
        delta = self.maxVal - self.minVal
        target = int(self.minVal + ((value / 1024) * delta))
        self.__pwm.duty_u16(target)

    def middle(self):
        self.goto(512)

    def free(self):
        self.__pwm.duty_u16(0)
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

