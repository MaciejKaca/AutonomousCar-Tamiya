from utils.conversion import Converter
from parts.pwm_driver import PWMDriver
import time

from utils.connection import Connection
from autonomousCarConnection.messages import SpeedData
from autonomousCarConnection.messages import Direction


class ESCMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Speed:
    direction: Direction = Direction.FORWARD
    speed: int = 0

    def __init__(self, direction: Direction = Direction.FORWARD, speed: int = 0):
        self.direction = direction
        self.speed = speed


class ESC(metaclass=ESCMeta):
    __MIN_TARGET_PWM = int(1000)
    __MAX_TARGET_PWM = int(2000)

    MAX_SPEED = int((__MAX_TARGET_PWM - __MIN_TARGET_PWM) / 2)
    MIN_SPEED = int(0)

    def __init__(self):
        self.__pwmDriver = PWMDriver()
        self.__ESC_CHANNEL_ID = 3

        self.__MIN_PWM_VALUE = int(0)
        self.__MAX_PWM_VALUE = int(10000)

        self.__MIN_PWM_DRIVER_VALUE = 0x0000
        self.__MAX_PWM_DRIVER_VALUE = 0xFFFF

        self.__NEUTRAL_TARGET_PWM = int(1500)
        self.__PWM_THRESHOLD = int(40)
        self.__PWM_TARGET_FOR_EACH_SIDE = (self.__MAX_TARGET_PWM - self.__MIN_TARGET_PWM) / 2

        self.__ESCChannel = self.__pwmDriver.get_channel(self.__ESC_CHANNEL_ID)

        self.__fromSpeedToPWM = Converter(self.MIN_SPEED, self.MAX_SPEED, 0, self.__PWM_TARGET_FOR_EACH_SIDE)
        self.__fromPwmToValueDriver = Converter(self.__MIN_PWM_VALUE, self.__MAX_PWM_VALUE, self.__MIN_PWM_DRIVER_VALUE,
                                                self.__MAX_PWM_DRIVER_VALUE)

        self.__sock = Connection()

        self.__speed: Speed = Speed()

        self.set_neutral()

    def __del__(self):
        self.set_neutral()

    def __valid_speed(self, target_speed: int, direction: Direction):
        if self.MIN_SPEED <= target_speed <= self.MAX_SPEED:
            if self.__speed.speed != target_speed or self.__speed.direction != direction:
                return True
            else:
                return False
        else:
            return False

    def set_speed_forward(self, target_speed: int):
        if self.__valid_speed(target_speed, Direction.FORWARD):
            self.__set_pwm(target_speed, Direction.FORWARD)

    def set_speed_backward(self, target_speed: int):
        if self.__valid_speed(target_speed, Direction.BACKWARD):
            if target_speed > 0:
                if self.__speed.direction != Direction.BACKWARD:
                    pwm = self.__NEUTRAL_TARGET_PWM + self.__PWM_THRESHOLD + 50
                    target_value = self.__fromPwmToValueDriver.get_target_value(pwm)
                    self.__ESCChannel.duty_cycle = int(target_value)
                    time.sleep(0.05)
                    target_value = self.__fromPwmToValueDriver.get_target_value(self.__NEUTRAL_TARGET_PWM)
                    self.__ESCChannel.duty_cycle = int(target_value)
                    time.sleep(0.05)

                self.__set_pwm(target_speed, Direction.BACKWARD)
            else:
                self.set_neutral()

    def brake(self, force: int):
        if self.__valid_speed(force, Direction.BRAKE):
            if force > 0:
                if self.__speed.direction != Direction.BRAKE:
                    target_value = self.__fromPwmToValueDriver.get_target_value(
                        self.__NEUTRAL_TARGET_PWM - self.__PWM_THRESHOLD)
                    self.__ESCChannel.duty_cycle = int(target_value)
                    time.sleep(0.1)

                self.__set_pwm(force, Direction.BRAKE)
            else:
                self.set_neutral()

    def set_neutral(self):
        self.__set_pwm(0, Direction.FORWARD)

    def __set_pwm(self, speed: int, direction: Direction):
        if direction == Direction.FORWARD:
            pwm = self.__fromSpeedToPWM.get_target_value(speed)
            pwm = self.__NEUTRAL_TARGET_PWM - pwm
            target_value = self.__fromPwmToValueDriver.get_target_value(pwm)
        else:
            pwm = self.__fromSpeedToPWM.get_target_value(abs(speed))
            pwm = self.__NEUTRAL_TARGET_PWM + pwm
            target_value = self.__fromPwmToValueDriver.get_target_value(pwm)

        self.__speed = Speed(direction, speed)
        self.__ESCChannel.duty_cycle = int(target_value)

        self.__send_telemetry()

    def __send_telemetry(self):
        speed_data = SpeedData()
        speed_opposite = SpeedData()

        if self.__speed.direction == Direction.BRAKE:
            speed_data.speed.value = self.__speed.speed
            speed_data.direction.value = Direction.BRAKE.value

            speed_opposite.speed.value = 0
            speed_opposite.direction.value = Direction.FORWARD.value
        else:
            speed_data.speed.value = self.__speed.speed
            speed_data.direction.value = self.__speed.direction.value

            speed_opposite.speed.value = 0
            speed_opposite.direction.value = Direction.BRAKE.value

        self.__sock.add_to_queue(speed_data)
        self.__sock.add_to_queue(speed_opposite)
