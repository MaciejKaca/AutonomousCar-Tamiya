from parts.esc import ESC
from parts.wheel import Wheel
from utils.conversion import Converter
from autonomousCarConnection.messages import JoystickData
import threading
from threading import Lock
from utils.connection import Connection


class SteamDeckInputMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SteamDeckInput(metaclass=SteamDeckInputMeta):
    def __init__(self) -> None:
        self.__wheel = Wheel()
        self.__esc = ESC()

        self.__keepRunning = True

        self.__AXIS_EVENT = 1536
        self.__BUTTON_UP_EVENT = 1540
        self.__BUTTON_DOWN_EVENT = 1539

        self.__RIGHT_TRIGGER = 5
        self.__LEFT_TRIGGER = 2
        self.__LEFT_BUTTON = 4
        self.__LEFT_AXIS = 0
        self.__START_BUTTON = 7

        self.__AXIS_MAX_VALUE = int(100)
        self.__AXIS_MIN_VALUE = int(-100)

        self.__AXIS_DEAD_ZONE = 0.4
        self.__TRIGGER_DEAD_ZONE = 0.2

        self.__fromXtoSpeed = Converter(self.__AXIS_MIN_VALUE, self.__AXIS_MAX_VALUE, ESC.MIN_SPEED, ESC.MAX_SPEED)
        self.__fromXtoAngle = Converter(self.__AXIS_MIN_VALUE, self.__AXIS_MAX_VALUE, Wheel.MIN_ANGLE, Wheel.MAX_ANGLE)
        self.__fromXtoAxis = Converter(-1 + self.__TRIGGER_DEAD_ZONE, 1, self.__AXIS_MIN_VALUE, self.__AXIS_MAX_VALUE)

        self.__BUTTON_DOWN = True
        self.__BUTTON_UP = False

        self.__axis_state = {self.__LEFT_AXIS: self.__AXIS_MIN_VALUE, self.__RIGHT_TRIGGER: self.__AXIS_MIN_VALUE,
                             self.__LEFT_TRIGGER: self.__AXIS_MIN_VALUE}
        self.__button_state = {self.__LEFT_BUTTON: self.__BUTTON_UP}

        self.__keepRunning_mutex = Lock()
        self.__socket = Connection()

        self.__pad_thread = threading.Thread(target=self.__handle_events, args=(), daemon=True)
        self.__pad_thread.start()

    def __del__(self):
        self.__keepRunning = False
        self.__pad_thread.join()
        self.__esc.set_neutral()

    def __get_trigger_value(self, x):
        if x > -1.0 + self.__TRIGGER_DEAD_ZONE:
            return self.__fromXtoAxis.get_target_value(x)
        return self.__AXIS_MIN_VALUE

    def __get_axis_value(self, x):
        if x < 0:
            return int(round((1 * min(0, x + self.__AXIS_DEAD_ZONE)) / (1 - self.__AXIS_DEAD_ZONE) * 100))
        return int(round((1 * max(0, x - self.__AXIS_DEAD_ZONE)) / (1 - self.__AXIS_DEAD_ZONE) * 100))

    def __handle_triggers(self):
        left_trigger_value = int(self.__axis_state.get(self.__LEFT_TRIGGER))
        right_trigger_value = int(self.__axis_state.get(self.__RIGHT_TRIGGER))

        if left_trigger_value > self.__AXIS_MIN_VALUE:
            speed = int(self.__fromXtoSpeed.get_target_value(left_trigger_value))
            if bool(self.__button_state.get(self.__LEFT_BUTTON)):
                self.__esc.set_speed_backward(speed)
            else:
                self.__esc.brake(speed)
        else:
            speed = int(self.__fromXtoSpeed.get_target_value(right_trigger_value))
            self.__esc.set_speed_forward(speed)

    def __handle_axis(self):
        value = self.__axis_state.get(self.__LEFT_AXIS)
        angle = self.__fromXtoAngle.get_target_value(value)
        self.__wheel.set_angle(angle)

    def __handle_button(self, event: JoystickData):
        button = event.button.value

        if button == self.__LEFT_BUTTON:
            self.__handle_triggers()

        elif button == self.__START_BUTTON:
            self.__keepRunning_mutex.acquire()
            self.__keepRunning = False
            self.__keepRunning_mutex.release()

    def was_exit_pressed(self) -> bool:
        self.__keepRunning_mutex.acquire()
        temp_value = self.__keepRunning
        self.__keepRunning_mutex.release()
        return not temp_value

    def __handle_events(self):
        while not self.was_exit_pressed():
            event: JoystickData = self.__socket.incomingJoystickQueue.get()

            if event.eventType.value == self.__AXIS_EVENT:
                axis = event.axis.value
                axis_value = event.inputValue.value
                value = self.__get_axis_value(axis_value)
                self.__axis_state[axis] = value

                if axis == self.__LEFT_TRIGGER or axis == self.__RIGHT_TRIGGER:
                    value = self.__get_trigger_value(axis_value)
                    self.__axis_state[axis] = value
                    self.__handle_triggers()
                else:
                    if axis == self.__LEFT_AXIS:
                        value = self.__get_axis_value(axis_value)
                        self.__axis_state[axis] = value
                        self.__handle_axis()
            else:
                button = event.button.value
                is_pressed = (event.eventType.value == self.__BUTTON_DOWN_EVENT)
                self.__button_state[button] = bool(is_pressed)
                self.__handle_button(event)
