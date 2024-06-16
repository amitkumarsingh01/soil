from machine import Pin

class MotorDriver:
    def __init__(self, pin1: int, pin2: int, pin3: int, pin4: int):
        self.pin1 = Pin(pin1, Pin.OUT)  # IN1 for Motor A
        self.pin2 = Pin(pin2, Pin.OUT)  # IN2 for Motor A
        self.pin3 = Pin(pin3, Pin.OUT)  # IN3 for Motor B
        self.pin4 = Pin(pin4, Pin.OUT)  # IN4 for Motor B

    def set_speed(self, speed: int):
        if speed < -100:
            speed = -100
        if speed > 100:
            speed = 100

        if speed > 10:
            # Reverse direction
            self.pin1.off()
            self.pin2.on()
            self.pin3.off()
            self.pin4.on()
        elif speed < -10:
            # Forward direction
            self.pin1.on()
            self.pin2.off()
            self.pin3.on()
            self.pin4.off()
        else:
            self.pin1.off()
            self.pin2.off()
            self.pin3.off()
            self.pin4.off()
