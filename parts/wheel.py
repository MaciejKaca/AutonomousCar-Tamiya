from configparser import ConverterMapping
from adafruit_motor import servo
from parts.pwm_driver import PWMDriver
from utils.conversion import Converter

class WheelMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Wheel(metaclass=WheelMeta):
    __STEERING_ANGLE = int(50)
    __MIDDLE_ANGLE = int(78)

    __MIN_ANGLE = int(__MIDDLE_ANGLE - __STEERING_ANGLE)
    __MAX_ANGLE = int(__MIDDLE_ANGLE + __STEERING_ANGLE)

    MAX_ANGLE = int((__MAX_ANGLE-__MIN_ANGLE)/2)
    MIN_ANGLE = int(-MAX_ANGLE)

    def __init__(self):
        self.__SERVO_CHANNEL_ID = 0
        self.__pwmDriver = PWMDriver()
        self.__wheelServo = servo.Servo(self.__pwmDriver.getChannel(self.__SERVO_CHANNEL_ID))
        self.__angle = int(0)

        self.__STEERING_ANGLE = int(50)
        self.__MIDDLE_ANGLE = int(78)

        self.__angleToServoAngle = Converter(self.MIN_ANGLE, self.MAX_ANGLE, self.__MIN_ANGLE, self.__MAX_ANGLE)

    def __del__(self):
        self.setAngle(0)

    def __validateAngle(self, angle: int) -> bool:
        if self.__angle != angle and self.MIN_ANGLE <= angle and angle <= self.MAX_ANGLE:
            return True
        else:
            return False

    def __validateTargetAngle(self, angle: int) -> bool:
        if self.__MIN_ANGLE <= angle and angle <= self.__MAX_ANGLE:
            return True
        else:
            return False
    
    def setAngle(self, angle: int):
        self.__setAngle(angle)
    
    def turnLeft(self, angle: int):
        if angle > int(0) and self.__validateAngle(angle):
            self.__setAngle(int(-1)*angle)
    
    def turnRight(self, angle: int):
        if angle > int(0) and self.__validateAngle(angle):
            self.__setAngle(angle)

    def goStraight(self):
        self.__setAngle(0)

    def __setAngle(self, angle: int):
        if self.__validateAngle(angle):
            converted = self.__angleToServoAngle.getTargetValue(angle)
            if self.__validateTargetAngle(converted):
                self.__angle = converted
                self.__wheelServo.angle = converted
