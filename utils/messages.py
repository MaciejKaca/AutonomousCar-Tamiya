from enum import Enum
import json
import time

from numpy import str0

class MessageType(Enum):
    NULL = 1
    SPEED = 2
    ANGLE = 3
    VOLATE = 4

class MessageFields(Enum):
    MESSAGE_TYPE = 1
    SENT_TYIME = 2
    DATA = 3

class DataMessage:
    def __init__(self):
        pass

    def get_time():
        return round(time.time() * 1000)

    def serialize(self) -> str:
        pass

    def deserialize(self):
        pass

    def __get_data(self):
        pass

class SpeedData(DataMessage):
    def __init__(self):
        self.speed = 0
        self.__MESSAGE_TYPE = MessageType.SPEED
        self.__SENT_TIME = DataMessage.get_time()

    def __get_data(self):
        data = {}
        data['speed'] = self.speed
        return data

    def __set_data(self, data : dict):
        self.speed = int(data.get('speed'))

    def serialize(self) -> str:
        data = self.__get_data()
        message = {MessageFields.MESSAGE_TYPE.name : self.__MESSAGE_TYPE.value, MessageFields.SENT_TYIME.name: self.__SENT_TIME, MessageFields.DATA.name: data}

        return str(message)

    def deserialize(self, message : str):
        message_dict = dict(message)
        self.__MESSAGE_TYPE = MessageType(message_dict.get(MessageFields.MESSAGE_TYPE.name))
        self.__SENT_TIME = int(message_dict.get(MessageFields.SENT_TYIME.name))

        data = dict(message_dict.get(MessageFields.DATA.name))
        self.__set_data(data)