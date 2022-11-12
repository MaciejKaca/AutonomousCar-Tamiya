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

class Speed():
    direction : Direction = Direction.FORWARD
    speed : int = 0

    def __init__(self, direction : Direction = Direction.FORWARD, speed : int = 0):
        self.direction = direction
        self.speed = speed

class ESC(metaclass=ESCMeta):
    __MIN_TARGET_PWM = int(1000)
    __MAX_TARGET_PWM = int(2000)

    MAX_SPEED = int((__MAX_TARGET_PWM-__MIN_TARGET_PWM)/2)
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
        self.__PWM_TARGET_FOR_EACH_SIDE = (self.__MAX_TARGET_PWM - self.__MIN_TARGET_PWM)/2

        self.__ESCChannel = self.__pwmDriver.getChannel(self.__ESC_CHANNEL_ID)

        self.__fromSpeedToPWM = Converter(self.MIN_SPEED, self.MAX_SPEED, 0, self.__PWM_TARGET_FOR_EACH_SIDE)
        self.__fromPwmToValueDriver = Converter(self.__MIN_PWM_VALUE, self.__MAX_PWM_VALUE, self.__MIN_PWM_DRIVER_VALUE, self.__MAX_PWM_DRIVER_VALUE)

        self.__sock = Connection()

        self.__speed : Speed = Speed()

        self.setNeutral()

    def __del__(self):
        self.setNeutral()

    def __validSpeed(self, targetSpeed : int, direction : Direction):
        if self.MIN_SPEED <= targetSpeed and targetSpeed <= self.MAX_SPEED:
            if self.__speed.speed != targetSpeed or self.__speed.direction != direction:
                return True
            else:
                return False
        else:
            return False

    def setSpeedForward(self, targetSpeed : int):
        if self.__validSpeed(targetSpeed, Direction.FORWARD):
            self.__setPwm(targetSpeed, Direction.FORWARD)

    def setSpeedBackward(self, targetSpeed : int):
        if self.__validSpeed(targetSpeed, Direction.BACKWARD):
            if targetSpeed > 0:
                if self.__speed.direction != Direction.BACKWARD:
                    pwm = self.__NEUTRAL_TARGET_PWM + self.__PWM_THRESHOLD + 50
                    targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
                    self.__ESCChannel.duty_cycle = int(targetValue)
                    time.sleep(0.05)
                    pwm = self.__NEUTRAL_TARGET_PWM
                    targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM)
                    self.__ESCChannel.duty_cycle = int(targetValue)
                    time.sleep(0.05)

                self.__setPwm(targetSpeed, Direction.BACKWARD)
            else:
                self.setNeutral()

    def brake(self, force : int):
        if self.__validSpeed(force, Direction.BRAKE):
            if force > 0:
                if self.__speed.direction != Direction.BRAKE:
                    targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM - self.__PWM_THRESHOLD)
                    self.__ESCChannel.duty_cycle = int(targetValue)
                    time.sleep(0.1)

                self.__setPwm(force, Direction.BRAKE)
            else:
                self.setNeutral()

    def setNeutral(self):
        self.__setPwm(0, Direction.FORWARD)

    def __setPwm(self, speed : int, direction : Direction):
        targetValue = 0

        if direction == Direction.FORWARD:
            pwm = self.__fromSpeedToPWM.getTargetValue(speed)
            pwm = self.__NEUTRAL_TARGET_PWM - pwm
            targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
        else:
            pwm = self.__fromSpeedToPWM.getTargetValue(abs(speed))
            pwm = self.__NEUTRAL_TARGET_PWM + pwm
            targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)

        self.__speed = Speed(direction, speed)
        self.__ESCChannel.duty_cycle = int(targetValue)

        self.__sendTelemetry()
    
    def __sendTelemetry(self):
        speedData = SpeedData()
        speedZero = SpeedData()

        if self.__speed.direction == Direction.BRAKE:
            speedData.speed = self.__speed.speed
            speedData.direction = Direction.BRAKE

            speedZero.speed = 0
            speedZero.direction = Direction.FORWARD
        else:
            speedData.speed = self.__speed.speed
            speedData.direction = self.__speed.direction

            speedZero.speed = 0
            speedZero.direction = Direction.BRAKE

        self.__sock.add_to_queue(speedData)
        self.__sock.add_to_queue(speedZero)