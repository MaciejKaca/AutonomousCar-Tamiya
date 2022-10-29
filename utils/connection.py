import socket
import queue, threading
from typing import List
from parts.steamdeck_input import SteamdeckInput
from autonomousCarConnection.messages import DataMessage, JoystickData, deserialize_message, MessageType

class ConnectionMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Connection(metaclass=ConnectionMeta):
    def __init__(self) -> None:
        self.__IS_CLIENT = False
        self.__CLIENT_ADDRESS = "192.168.0.53"
        self.__CAR_ADDRESS = "192.168.0.115"
        self.__LOCAL_PORT   = 5555
        self.__bufferSize  = 1024
        self.__UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__UDPSocket.settimeout(10)
        self.__isConnected = False
        self.__message_send_queue = queue.Queue()
        self.__message_recv_queue = queue.Queue()
        self.__joystick = SteamdeckInput()

        if not self.__IS_CLIENT:
            self.__UDPSocket.settimeout(10)

        self.__init_conection()
        
        if self.__isConnected:
            self.__recv_thread = threading.Thread(target=self.__recv, args=(), daemon=True)
            self.__send_thread = threading.Thread(target=self.__send, args=(), daemon=True)
            self.__recv_thread.start()
            self.__send_thread.start()

    def __del__(self):
        if self.__isConnected:
            self.__UDPSocket.close()
            self.__isConnected = False
            self.__recv_thread.join()
            self.__send_thread.join()

    def __init_conection(self):
        try:
            if self.__IS_CLIENT:
                print("Waiting for client")
                self.__UDPSocket.bind((self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
                bytesAddressPair = self.__UDPSocket.recvfrom(self.__bufferSize)
                addr = bytesAddressPair[1]
                print("Connected to: ", addr)
                self.__isConnected = True
            else:
                print("Sending Hello to :", (self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
                self.__UDPSocket.bind((self.__CAR_ADDRESS, self.__LOCAL_PORT))
                bytesToSend = str.encode("Hello")
                self.__UDPSocket.sendto(bytesToSend, (self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
                self.__isConnected = True
            self.__UDPSocket.settimeout(None)
        except socket.timeout as e:
            print("Failed to connect")
            self.__isConnected = False

    def add_to_queue(self, message : DataMessage):
        if self.__isConnected:
            print("Sending message: " + message.serialize())
            self.__message_send_queue.put(message.serialize())
    
    def get_data(self) -> List[DataMessage]:
        data_list = []
        while not self.__message_recv_queue.empty():
            data  = self.__message_recv_queue.get()
            data_list.append(data)
        return data_list

    def __send(self):
        while self.__isConnected:
            message = self.__message_send_queue.get()
            bytesToSend = str.encode(message)
            if self.__IS_CLIENT:
                self.__UDPSocket.sendto(bytesToSend, (self.__CAR_ADDRESS, self.__LOCAL_PORT))
            else:
                self.__UDPSocket.sendto(bytesToSend, (self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
    
    def __recv(self):
        while self.__isConnected:
            message = self.__UDPSocket.recvfrom(self.__bufferSize)
            data = deserialize_message(message[0])
            self.__handle_message(data)
            self.__message_recv_queue.put(data)

    def __handle_message(self, message : DataMessage):
        if message.message_type == MessageType.JOYSTICK:
            self.__joystick.add_event(message)