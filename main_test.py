from parts.esc import ESC
from parts.wheel import Wheel
from parts.pwm_driver import PWMDriver
from parts.steamdeck_input import SteamdeckInput
from utils.connection import Connection
import time

clientSocket = Connection()
input = SteamdeckInput()
pwm_driver = PWMDriver()
wheel = Wheel()
esc = ESC()

esc.setSpeedForward(0)
wheel.setAngle(0)

while not input.was_exit_pressed():
  time.sleep(1)