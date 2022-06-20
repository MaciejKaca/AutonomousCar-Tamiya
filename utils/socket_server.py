import socket
import queue, threading
from threading import Condition
import json
import time

from utils.messages import DataMessage

class CarSocketMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class CarSocket(metaclass=CarSocketMeta):
    def __init__(self) -> None:
        self.__localIP     = "192.168.0.115"
        self.__localPort   = 5555
        self.__bufferSize  = 1024
        self.__UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__UDPServerSocket.bind((self.__localIP, self.__localPort))
        self.__client_address = ""
        self.__UDPServerSocket.settimeout(10)
        self.__isConnected = False
        self.__message_queue = queue.Queue()

        self.__init_conection()
        
        if self.__isConnected:
            self.__socket_thread = threading.Thread(target=self.__send, args=(), daemon=True)
            self.__socket_thread.start()

    def __del__(self):
        if self.__isConnected:
            self.__isConnected = False
            self.__socket_thread.join()

    def __init_conection(self):
        try:
            bytesAddressPair = self.__UDPServerSocket.recvfrom(self.__bufferSize)
            self.__client_address = bytesAddressPair[1]
            print("Connected to: ", self.__client_address)
            self.__isConnected = True
        except socket.timeout as e:
            print("Failed to connect")
            self.__isConnected = False

    def add_to_queue(self, message : DataMessage):
        if self.__isConnected:
            self.__message_queue.put(message.serialize())

    def __send(self):
        while self.__isConnected:
            message = self.__message_queue.get()
            bytesToSend = str.encode(message)
            self.__UDPServerSocket.sendto(bytesToSend, self.__client_address)