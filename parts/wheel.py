from adafruit_motor import servo
from pwm_driver import PWMDriver

class WheelMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Wheel(metaclass=WheelMeta):
    __SERVO_CHANNEL_ID = 0
    __pwmDriver = PWMDriver()
    __wheelServo = servo.Servo(__pwmDriver.getChannel(__SERVO_CHANNEL_ID))
    __angle = int(0)
    MAX_ANGLE = int(50)
    MIN_ANGLE = int(-50)
    MIDDLE_ANGLE = int(0)
    __MIN_ANGLE = int(40)
    __MAX_ANGLE = int(140)

    def validateAngle(self, angle: int) -> bool:
        if self.MIN_ANGLE <= angle and angle <= self.MIN_ANGLE:
            return True
        else:
            return False

    def validateTargetAngle(self, angle: int) -> bool:
        if self.__MIN_ANGLE <= angle and angle <= self.__MAX_ANGLE:
            return True
        else:
            return False
    
    def setAngle(self, angle: int):
        if self.validateAngle(angle):
            self.__wheelServo.angle(angle)
    
    def turnLeft(self, angle: int):
        if angle > int(0) and self.validateAngle(angle):
            self.__wheelServo.angle(int(-1)*angle)
    
    def turnRight(self, angle: int):
        if angle > int(0) and self.validateAngle(angle):
            self.__wheelServo.angle(angle)

    def goStraight(self):
        self.__wheelServo.angle(0)

    def convertAngle(self, angle: int):
        return self.__MAX_ANGLE + ((abs(self.MIN_ANGLE) + angle) / (self.__MAX_ANGLE - self.__MIN_ANGLE))

    def __setAngle(self, angle: int):
        if self.validateAngle(angle):
            converted = self.convertAngle(angle)
            if self.validateTargetAngle(converted):
                self.__wheelServo.angle(converted)