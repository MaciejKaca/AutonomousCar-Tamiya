from enum import Enum
import time
import json

class MessageType(Enum):
    NULL = 1
    SPEED = 2
    ANGLE = 3
    VOLAGE = 4

class MessageFields(Enum):
    MESSAGE_TYPE = 1
    SENT_TYIME = 2
    DATA = 3

class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2
    BRAKE = 3

def deserialize_message(message):
    message = message.decode("utf-8")
    message_dict = dict(json.loads(message))
    message_type = MessageType(message_dict.get(MessageFields.MESSAGE_TYPE.name))

    if message_type == MessageType.SPEED:
        speed_data = SpeedData()
        speed_data.deserialize(message_dict)
        return speed_data

class DataMessage:
    def __init__(self):
        self.message_type = MessageType.NULL
        self.sent_time = self.get_time()
        pass

    def get_time():
        return round(time.time() * 1000)

    def serialize(self) -> str:
        pass

    def deserialize(self):
        pass

    def __get_data(self, message):
        pass

class SpeedData(DataMessage):
    def __init__(self):
        self.speed = 0
        self.direction = Direction.FORWARD
        self.message_type= MessageType.SPEED
        self.sent_time = DataMessage.get_time()

    def __get_data(self):
        data = {}
        data['speed'] = self.speed
        data['direction'] = self.direction.value
        return data

    def __set_data(self, data : dict):
        self.speed = int(data.get('speed'))
        self.direction = Direction(int(data.get('direction')))

    def serialize(self) -> str:
        data = self.__get_data()
        message = {MessageFields.MESSAGE_TYPE.name : self.message_type.value, MessageFields.SENT_TYIME.name: self.sent_time, MessageFields.DATA.name: data}

        return json.dumps(message)

    def deserialize(self, message):
        self.message_type = MessageType(message.get(MessageFields.MESSAGE_TYPE.name))
        self.sent_time = int(message.get(MessageFields.SENT_TYIME.name))

        data = dict(message.get(MessageFields.DATA.name))
        self.__set_data(data)