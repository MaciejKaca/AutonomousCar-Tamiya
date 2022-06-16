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
    keepRunning = True

    fromXtoSpeed = Converter(-100, 100, ESC.MIN_SPEED, ESC.MAX_SPEED)
    fromXtoAngle = Converter(-100, 100, Wheel.MIN_ANGLE, Wheel.MAX_ANGLE)

    wheel = Wheel()
    esc = ESC()

    RIGHT_TRIGGER = 5
    LEFT_TRIGGER = 2
    AXIS_EVENT = 7
    BUTTON_UP_EVENT = 11
    BUTTON_DOWN_EVENT = 10
    LEFT_BUTTON = 4
    LEFT_AXIS = 0

    left_trigger_value = int(100)

    AXIS_MAX_VALUE = int(100)
    AXIS_MIN_VALUE = int(-100)

    BUTTON_DOWN = True
    BUTTON_UP = False

    axis_state = {LEFT_AXIS : AXIS_MIN_VALUE, RIGHT_TRIGGER : AXIS_MIN_VALUE, LEFT_TRIGGER : AXIS_MIN_VALUE}
    button_state = {LEFT_BUTTON : BUTTON_UP}

    def __init__(self, controller, deadzone):
        self.controller = controller
        self.controller.init()
        self.deadzone = deadzone
        pad_thread = threading.Thread(target=self.handle_events, args=(), daemon=True)
        pad_thread.start()

    def __del__(self):
        self.keepRunning = False
        self.pad_thread.join()

    def axis_deadzone(self, x):
        if x < 0:
            return int(round((1 * min(0, x + self.deadzone)) / (1 - self.deadzone) * 100))
        return int(round((1 * max(0, x - self.deadzone)) / (1 - self.deadzone) * 100))

    def trigger_deadzone (self, x):
        return  int(round((x + 1) / 2 * 100))

    def get_axis_value(self, value):
        return (self.axis_deadzone(value))

    def get_button_value(self, button):
        for event in pygame.event.get():
            None
        return self.controller.get_button(button)

    def handle_triggers(self):
        left_trigger_value = int(self.axis_state.get(self.LEFT_TRIGGER))
        right_trigger_value = int(self.axis_state.get(self.RIGHT_TRIGGER))

        if left_trigger_value > self.AXIS_MIN_VALUE:
            speed = self.fromXtoSpeed.getTargetValue(left_trigger_value)
            if bool(self.button_state.get(self.LEFT_BUTTON)):
                self.esc.setSpeedBackward(speed)
            else:
                self.esc.brake(speed)
        else:
            speed = self.fromXtoSpeed.getTargetValue(right_trigger_value)
            self.esc.setSpeedForward(speed)

    def handle_axis(self):
        value = self.axis_state.get(self.LEFT_AXIS)
        angle = self.fromXtoAngle.getTargetValue(value)
        self.wheel.setAngle(angle)

    def handle_button(self, event : Event):
        button = event.__dict__.get('button')

        if button == self.LEFT_BUTTON:
            self.handle_triggers()           

    def handle_events(self):
        while self.keepRunning:
            for event in pygame.event.get():
                if event.type == self.AXIS_EVENT:
                    axis = event.__dict__.get('axis')
                    axis_value = event.__dict__.get('value')
                    value = self.get_axis_value(axis_value)
                    self.axis_state[axis] = value
                    
                    if axis == self.LEFT_TRIGGER or axis == self.RIGHT_TRIGGER:
                        self.handle_triggers()
                    else:
                        self.handle_axis()
                else:
                    button = event.__dict__.get('button')
                    isPressed = (event.type == self.BUTTON_DOWN_EVENT)
                    self.button_state[button] = bool(isPressed)

                    self.handle_button(event)
        time.sleep(0.05) #50ms