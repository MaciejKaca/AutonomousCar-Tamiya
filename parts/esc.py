from utils.conversion import Converter
from parts.pwm_driver import PWMDriver
import time

class ESCMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ESC(metaclass=ESCMeta):
    __pwmDriver = PWMDriver()
    __ESC_CHANNEL_ID = 3

    __MIN_PWM_VALUE = int(0)
    __MAX_PWM_VALUE = int(10000)

    __MIN_PWM_DRIVER_VALUE = 0x0000
    __MAX_PWM_DRIVER_VALUE = 0xFFFF

    __MIN_TARGET_PWM = int(500)
    __MAX_TARGET_PWM = int(2500)
    __NEUTRAL_TARGET_PWM = int(1500)
    __PWM_THRESHOLD = int(50)

    MAX_SPEED = int((__MAX_TARGET_PWM-__MIN_TARGET_PWM)/2)
    MIN_SPEED = int(0)

    __ESCChannel = __pwmDriver.getChannel(__ESC_CHANNEL_ID)

    __fromSpeedToForward = Converter(MIN_SPEED, MAX_SPEED, __NEUTRAL_TARGET_PWM, __MAX_TARGET_PWM)
    __fromSpeedToBackward= Converter(MIN_SPEED, MAX_SPEED, __MIN_TARGET_PWM, __NEUTRAL_TARGET_PWM)
    __fromPwmToValueDriver = Converter(__MIN_PWM_VALUE, __MAX_PWM_VALUE, __MIN_PWM_DRIVER_VALUE, __MAX_PWM_DRIVER_VALUE)

    wasBraking = False

    def __init__(self):
        pass

    def __validSpeed(self, targetSpeed : int):
        if self.MIN_SPEED <= targetSpeed and targetSpeed <= self.MAX_SPEED:
            return True
        else:
            return False

    def setSpeedForward(self, targetSpeed : int):
        if self.__validSpeed(targetSpeed):
            pwm = self.__fromSpeedToPwm.getTargetValue(-targetSpeed)
            targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
            self.__ESCChannel.duty_cycle = targetValue

    def setSpeedBackward(self, targetSpeed : int):
        if self.__validSpeed(targetSpeed):
            targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM + self.__PWM_THRESHOLD)
            self.__ESCChannel.duty_cycle = targetValue
            time.sleep(0.1)
            targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM - self.__PWM_THRESHOLD)
            self.__ESCChannel.duty_cycle = targetValue
            time.sleep(0.1)
            targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM)
            self.__ESCChannel.duty_cycle = targetValue
            time.sleep(0.1)

            pwm = self.__fromSpeedToPwm.getTargetValue(targetSpeed)
            targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
            self.__ESCChannel.duty_cycle = targetValue

    def brake(self, force : int):
        if self.__validSpeed(force):
            if self.wasBraking:
                targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM + self.__PWM_THRESHOLD)
                self.__ESCChannel.duty_cycle = targetValue
                time.sleep(0.1)

            pwm = self.__fromSpeedToPwm.getTargetValue(force)
            targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
            self.__ESCChannel.duty_cycle = targetValue

            if force > 0:
                self.wasBraking = True
            else:
                self.wasBraking = False

    def setNeutral(self):
        targetValue = self.__fromPwmToValueDriver.getTargetValue(self.__NEUTRAL_TARGET_PWM)
        self.__ESCChannel.duty_cycle = targetValue

    def __del__(self):
        self.setSpeed(0)