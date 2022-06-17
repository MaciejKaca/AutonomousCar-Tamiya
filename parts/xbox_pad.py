from multiprocessing import Event
from matplotlib.font_manager import ttfFontProperty
from matplotlib.pyplot import axis
from platformdirs import _set_platform_dir_class
import pygame

import subprocess
import os
import atexit

from parts.esc import ESC
from parts.wheel import Wheel
from utils.conversion import Converter
import threading
from threading import Lock
import time

pygame.init()
pygame.joystick.init()

def get_count():
  return pygame.joystick.get_count()

def get_controller(x):
  count = pygame.joystick.get_count()
  if count == 0:
    print("no joysticks connected")
    return None
  elif x < count:
    return Xcontroller(pygame.joystick.Joystick(x), 0.05)
  else:
    print("Joystick " + str(x) + " not connected")
    print("choose joystic from 0 to " + str(count -1))
    return None  

class Xcontroller:
    __keepRunning = True

    __fromXtoSpeed = Converter(-100, 100, ESC.MIN_SPEED, ESC.MAX_SPEED)
    __fromXtoAngle = Converter(-100, 100, Wheel.MIN_ANGLE, Wheel.MAX_ANGLE)

    __wheel = Wheel()
    __esc = ESC()

    __RIGHT_TRIGGER = 5
    __LEFT_TRIGGER = 2
    __AXIS_EVENT = 7
    __BUTTON_UP_EVENT = 11
    __BUTTON_DOWN_EVENT = 10
    __LEFT_BUTTON = 4
    __LEFT_AXIS = 0
    __START_BUTTON = 7

    __AXIS_MAX_VALUE = int(100)
    __AXIS_MIN_VALUE = int(-100)

    __BUTTON_DOWN = True
    __BUTTON_UP = False

    __axis_state = {__LEFT_AXIS : __AXIS_MIN_VALUE, __RIGHT_TRIGGER : __AXIS_MIN_VALUE, __LEFT_TRIGGER : __AXIS_MIN_VALUE}
    __button_state = {__LEFT_BUTTON : __BUTTON_UP}

    __keepRunning_mutex = Lock()

    def __init__(self, controller, deadzone):
        self.__controller = controller
        self.__controller.init()
        self.__deadzone = deadzone
        self.__pad_thread = threading.Thread(target=self.__handle_events, args=(), daemon=True)
        self.__pad_thread.start()

    def __del__(self):
        self.__keepRunning = False
        self.__pad_thread.join()
        self.__esc.setNeutral()

    def __axis_deadzone(self, x):
        if x < 0:
            return int(round((1 * min(0, x + self.__deadzone)) / (1 - self.__deadzone) * 100))
        return int(round((1 * max(0, x - self.__deadzone)) / (1 - self.__deadzone) * 100))

    def __trigger_deadzone (x):
        return  int(round((x + 1) / 2 * 100))

    def __get_axis_value(self, value):
        return (self.__axis_deadzone(value))

    def __handle_triggers(self):
        left_trigger_value = int(self.__axis_state.get(self.__LEFT_TRIGGER))
        right_trigger_value = int(self.__axis_state.get(self.__RIGHT_TRIGGER))

        if left_trigger_value > self.__AXIS_MIN_VALUE:
            speed = self.__fromXtoSpeed.getTargetValue(left_trigger_value)
            if bool(self.__button_state.get(self.__LEFT_BUTTON)):
                self.__esc.setSpeedBackward(speed)
            else:
                self.__esc.brake(speed)
        else:
            speed = self.__fromXtoSpeed.getTargetValue(right_trigger_value)
            self.__esc.setSpeedForward(speed)

    def __handle_axis(self):
        value = self.__axis_state.get(self.__LEFT_AXIS)
        angle = self.__fromXtoAngle.getTargetValue(value)
        self.__wheel.setAngle(angle)

    def __handle_button(self, event : Event):
        button = event.__dict__.get('button')

        if button == self.__LEFT_BUTTON:
            self.__handle_triggers()

        elif button == self.__START_BUTTON:
            self.__keepRunning_mutex.acquire()
            self.__keepRunning = False
            self.__keepRunning_mutex.release()

    def was_exit_pressed(self) -> bool:
        self.__keepRunning_mutex.acquire()
        tempValue = self.__keepRunning
        self.__keepRunning_mutex.release()
        return not tempValue

    def __handle_events(self):
        while not self.was_exit_pressed():
            for event in pygame.event.get():
                if event.type == self.__AXIS_EVENT:
                    axis = event.__dict__.get('axis')
                    axis_value = event.__dict__.get('value')
                    value = self.__get_axis_value(axis_value)
                    self.__axis_state[axis] = value
                    
                    if axis == self.__LEFT_TRIGGER or axis == self.__RIGHT_TRIGGER:
                        self.__handle_triggers()
                    else:
                        self.__handle_axis()
                else:
                    button = event.__dict__.get('button')
                    isPressed = (event.type == self.__BUTTON_DOWN_EVENT)
                    self.__button_state[button] = bool(isPressed)
                    self.__handle_button(event)
        time.sleep(0.1) #100ms