from adafruit_motor.servo import Servo
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

    MAX_ANGLE = int((__MAX_ANGLE - __MIN_ANGLE) / 2)
    MIN_ANGLE = int(-MAX_ANGLE)

    def __init__(self):
        self.__SERVO_CHANNEL_ID = 0
        self.__pwmDriver = PWMDriver()
        self.__wheelServo = Servo(self.__pwmDriver.get_channel(self.__SERVO_CHANNEL_ID))
        self.__angle = int(0)

        self.__STEERING_ANGLE = int(50)
        self.__MIDDLE_ANGLE = int(78)

        self.__angleToServoAngle = Converter(self.MIN_ANGLE, self.MAX_ANGLE, self.__MIN_ANGLE, self.__MAX_ANGLE)

    def __del__(self):
        self.set_angle(0)

    def __validate_angle(self, angle: int) -> bool:
        if self.__angle != angle\
                and self.MIN_ANGLE <= angle <= self.MAX_ANGLE:
            return True
        else:
            return False

    def __validate_target_angle(self, angle: int) -> bool:
        if self.__MIN_ANGLE <= angle <= self.__MAX_ANGLE:
            return True
        else:
            return False

    def set_angle(self, angle: int):
        self.__set_angle(angle)

    def turn_left(self, angle: int):
        if angle > int(0) and self.__validate_angle(angle):
            self.__set_angle(int(-1) * angle)

    def turn_right(self, angle: int):
        if angle > int(0) and self.__validate_angle(angle):
            self.__set_angle(angle)

    def go_straight(self):
        self.__set_angle(0)

    def __set_angle(self, angle: int):
        if self.__validate_angle(angle):
            converted = self.__angleToServoAngle.get_target_value(angle)
            if self.__validate_target_angle(converted):
                self.__angle = converted
                self.__wheelServo.angle = converted
