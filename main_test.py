from multiprocessing import Event
from matplotlib.font_manager import ttfFontProperty
import pygame

import subprocess
import os
import atexit

from parts.esc import ESC
from parts.wheel import Wheel
from utils.conversion import Converter
import parts.xbox_pad as Xbox


clock = pygame.time.Clock()

import time

pad1 = Xbox.get_controller(0)
wheel = Wheel()
esc = ESC()

esc.setSpeedForward(0)
wheel.setAngle(0)

fromXtoSpeed = Converter(-100, 100, esc.MIN_SPEED, esc.MAX_SPEED)
fromXtoAngle = Converter(-100, 100, wheel.MIN_ANGLE, wheel.MAX_ANGLE)

while True:
  time.sleep(1)
  clock.tick(10)