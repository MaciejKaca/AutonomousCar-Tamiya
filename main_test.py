from parts.esc import ESC
from parts.wheel import Wheel
from parts.pwm_driver import PWMDriver
from parts.steamdeck_input import SteamdeckInput
import  autonomousCarConnection.connection as ClientSocket
import time

clientSocket = ClientSocket.Connection(is_server=False)
input = SteamdeckInput()
pwm_driver = PWMDriver()
wheel = Wheel()
esc = ESC()

esc.setSpeedForward(0)
wheel.setAngle(0)

while not input.was_exit_pressed():
  time.sleep(1)