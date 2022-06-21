from multiprocessing import Event
from matplotlib.font_manager import ttfFontProperty
import pygame

from utils.messages import *
from parts.esc import ESC
from parts.wheel import Wheel
from parts.pwm_driver import PWMDriver
import parts.xbox_pad as Xbox

clock = pygame.time.Clock()

import time

pad1 = Xbox.get_controller(0)
pwm_driver = PWMDriver()
wheel = Wheel()
esc = ESC()

esc.setSpeedForward(0)
wheel.setAngle(0)

while not pad1.was_exit_pressed():
  time.sleep(1)