from socket import socket
from parts.esc import ESC
from parts.wheel import Wheel
from parts.pwm_driver import PWMDriver
from parts.steamdeck_input import SteamDeckInput
from utils.connection import Connection
import time

clientSocket = Connection()
clientSocket.wait_for_client()
steamDeckInput = SteamDeckInput()
pwm_driver = PWMDriver()
wheel = Wheel()
esc = ESC()

esc.set_speed_forward(0)
wheel.set_angle(0)

while not steamDeckInput.was_exit_pressed() and clientSocket.is_client_connected():
    time.sleep(1)
