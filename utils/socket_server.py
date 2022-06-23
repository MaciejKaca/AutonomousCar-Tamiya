import socket
import queue, threading
from typing import List

from utils.messages import DataMessage, deserialize_message

class CarSocketMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class CarSocket(metaclass=CarSocketMeta):
    def __init__(self) -> None:
        self.__is_server = True
        self.__localIP     = "192.168.0.115"
        self.__localPort   = 5555
        self.__bufferSize  = 1024
        self.__UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__partner_address = self.__localIP
        self.__UDPSocket.settimeout(10)
        self.__isConnected = False
        self.__message_send_queue = queue.Queue()
        self.__message_recv_queue = queue.Queue()

        self.__init_conection()
        
        if self.__isConnected:
            if self.__is_server:
                self.__socket_thread = threading.Thread(target=self.__send, args=(), daemon=True)
            else:
                self.__socket_thread = threading.Thread(target=self.__recv, args=(), daemon=True)
            self.__socket_thread.start()

    def __del__(self):
        if self.__isConnected:
            self.__isConnected = False
            self.__socket_thread.join()

    def __init_conection(self):
        try:
            if self.__is_server:
                print("Waiting for client")
                self.__UDPSocket.bind((self.__localIP, self.__localPort))
                bytesAddressPair = self.__UDPSocket.recvfrom(self.__bufferSize)
                self.__partner_address = bytesAddressPair[1]
                print("Connected to: ", self.__partner_address)
                self.__isConnected = True
            else:
                bytesToSend = str.encode("Hello")
                self.__UDPSocket.sendto(bytesToSend, (self.__partner_address, self.__localPort))
                self.__isConnected = True
            self.__UDPSocket.settimeout(None)
        except socket.timeout as e:
            print("Failed to connect")
            self.__isConnected = False

    def add_to_queue(self, message : DataMessage):
        if self.__isConnected:
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
            self.__UDPSocket.sendto(bytesToSend, self.__partner_address)
    
    def __recv(self):
        while self.__isConnected:
            message = self.__UDPSocket.recvfrom(self.__bufferSize)
            data = deserialize_message(message[0])
            self.__message_recv_queue.put(data)