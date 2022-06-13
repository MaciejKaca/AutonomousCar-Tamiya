from utils.conversion import Converter
from parts.pwm_driver import PWMDriver

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

    MAX_SPEED = int((__MAX_TARGET_PWM-__MIN_TARGET_PWM)/2)
    MIN_SPEED = int(-MAX_SPEED)

    __ESCChannel = __pwmDriver.getChannel(__ESC_CHANNEL_ID)

    __fromSpeedToPwm = Converter(MIN_SPEED, MAX_SPEED, __MIN_TARGET_PWM, __MAX_TARGET_PWM)
    __fromPwmToValueDriver = Converter(__MIN_PWM_VALUE, __MAX_PWM_VALUE, __MIN_PWM_DRIVER_VALUE, __MAX_PWM_DRIVER_VALUE)

    def __init__(self):
        pass

    def setSpeed(self, targetSpeed : int):
        pwm = self.__fromSpeedToPwm.getTargetValue(-targetSpeed)
        targetValue = self.__fromPwmToValueDriver.getTargetValue(pwm)
        self.__ESCChannel.duty_cycle = targetValue

    def __del__(self):
        self.setSpeed(0)