from multiprocessing import Event
from matplotlib.font_manager import ttfFontProperty
import pygame

import subprocess
import os
import atexit

from parts.esc import ESC
from parts.wheel import Wheel
from parts.pwm_driver import PWMDriver
import parts.xbox_pad as Xbox

from utils.socket_server import CarSocket
from utils.messages import *

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