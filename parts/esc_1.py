# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# This simple test outputs a 50% duty cycle PWM single on the 0th channel. Connect an LED and
# resistor in series to the pin to visualize duty cycle changes and its impact on brightness.

from board import SCL, SDA
import busio
import time
# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685


def targetPwm(pwm):
    maxPwm = int(10000)
    scale = float(0xFFFF/maxPwm)
    targetPwm = int(0xFFFF - ((maxPwm - pwm) * scale))
    print(targetPwm)
    return targetPwm

# Create the I2C bus interface.
i2c_bus = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c_bus, address=0x41, reference_clock_speed=25395200)
pca.reset()

# Set the PWM frequency to 60hz.
pca.frequency = 100
esc_channel = pca.channels[3]

if True:
    esc_channel.duty_cycle = targetPwm(1350)
    time.sleep(1)
    esc_channel.duty_cycle = targetPwm(2000)
    time.sleep(1)
    esc_channel.duty_cycle = targetPwm(1500)
    time.sleep(1)
    esc_channel.duty_cycle = targetPwm(1580)
    time.sleep(2)
    esc_channel.duty_cycle = targetPwm(1460)
    time.sleep(0.1)
    esc_channel.duty_cycle = targetPwm(2000)
    time.sleep(1)
    esc_channel.duty_cycle = targetPwm(1500)





