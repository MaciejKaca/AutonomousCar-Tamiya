from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685, PWMChannel


class PWMDriverMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(PWMDriverMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PWMDriver(metaclass=PWMDriverMeta):
    def __init__(self):
        self.__i2c = busio.I2C(SCL, SDA)
        self.__pca = PCA9685(self.__i2c, address=0x41, reference_clock_speed=25395200)

        self.__pca.reset()
        self.__pca.frequency = 100

    def __del__(self):
        self.__pca.deinit()

    def get_channel(self, channel_id) -> PWMChannel:
        return self.__pca.channels[channel_id]
