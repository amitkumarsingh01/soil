from machine import Pin

class LinearActuator:
    def __init__(self, pin1: int, pin2: int):
        self.pin1 = Pin(pin1, Pin.OUT)
        self.pin2 = Pin(pin2, Pin.OUT)

    def control(self, value: int):
        if value == 50:
            # Rotate clockwise
            self.pin1.off()
            self.pin2.on()
        elif value == 100:
            # Rotate anticlockwise
            self.pin1.on()
            self.pin2.off()
        else:
            # Stop
            self.pin1.off()
            self.pin2.off()
