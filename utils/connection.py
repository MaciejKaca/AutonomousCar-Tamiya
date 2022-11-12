import socket
import queue, threading
from threading import Lock
from typing import List
from autonomousCarConnection.messages import DataMessage, Heartbeat, JoystickData, deserialize_message, MessageType
import time

class ConnectionMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Connection(metaclass=ConnectionMeta):
    def __init__(self) -> None:
        self.__CAR_SYSTEM_ID = 111
        self.__CLIENT_SYSTEM_ID = 222
        self.__HEARTBEAT_HZ = 1
        self.__UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.__CLIENT_ADDRESS = "192.168.0.122"
        self.__CAR_ADDRESS = "192.168.0.115"
        self.__LOCAL_PORT   = 5555
        self.__bufferSize  = 1024
        self.__isConnected = False
        self.__message_send_queue = queue.Queue()
        self.__message_recv_queue = queue.Queue()
        self.__keep_running = True
        self.__last_hearbeat_time = 0
        self.__HEARTBEAT_TIMEOUT = 2000 # 2 seconds
        self.__HEARTBEAT_MONITOR_REFHRES_TIME = 2 # 2 seconds

        self.__UDPSocket.bind((self.__CAR_ADDRESS, self.__LOCAL_PORT))
        self.__hearbeat_mutex = Lock()

        self.__recv_thread = threading.Thread(target=self.__recv, args=(), daemon=True)
        self.__send_thread = threading.Thread(target=self.__send, args=(), daemon=True)
        self.__hearbeat_thread = threading.Thread(target=self.__send_hearbeat, args=(), daemon=True)
        self.__monitor_hearbeat_thread = threading.Thread(target=self.__monitor_heartbeat, args=(), daemon=True)
        self.__recv_thread.start()
        self.__send_thread.start()
        self.__hearbeat_thread.start()
        self.__monitor_hearbeat_thread.start()

        self.incoming_joystick_queue = queue.Queue()

    def __del__(self):
        if self.__isConnected:
            self.__UDPSocket.close()
            self.__isConnected = False
            self.__keep_running = False
            self.__recv_thread.join()
            self.__send_thread.join()
            self.__hearbeat_thread.join()
            self.__monitor_hearbeat_thread.join()

    def add_to_queue(self, message : DataMessage):
        self.__message_send_queue.put(message.serialize())

    def get_data(self) -> List[DataMessage]:
        data_list = []
        while not self.__message_recv_queue.empty():
            data  = self.__message_recv_queue.get()
            data_list.append(data)
        return data_list

    def __send(self):
        while self.__keep_running:
            message = self.__message_send_queue.get()
            bytesToSend = str.encode(message)
            self.__UDPSocket.sendto(bytesToSend, (self.__CLIENT_ADDRESS, self.__LOCAL_PORT))
    
    def __recv(self):
        while self.__keep_running:
            message = self.__UDPSocket.recvfrom(self.__bufferSize)
            data = deserialize_message(message[0])
            self.__handle_message(data)
            self.__message_recv_queue.put(data)

    def __handle_message(self, message : DataMessage):
        if message.message_type == MessageType.JOYSTICK:
            self.incoming_joystick_queue.put(message)
        elif message.message_type == MessageType.HEARTBEAT:
            hearbeat : Heartbeat = message
            if hearbeat.system_id == self.__CLIENT_SYSTEM_ID:
                self.__hearbeat_mutex.acquire
                self.__last_hearbeat_time = self.__get_time()
                self.__hearbeat_mutex.release

    def __send_hearbeat(self):
        while self.__keep_running:
            hearbeat = Heartbeat()
            hearbeat.system_id = self.__CAR_SYSTEM_ID
            self.add_to_queue(hearbeat)
            time.sleep(self.__HEARTBEAT_HZ)

    def __monitor_heartbeat(self):
        while self.__keep_running:
            self.__hearbeat_mutex.acquire
            if (self.__get_time() - self.__last_hearbeat_time) < self.__HEARTBEAT_TIMEOUT:
                if not self.__isConnected:
                    print("Connected to client")
                self.__isConnected = True
            else:
                if self.__isConnected:
                    print("Client disconected")
                self.__isConnected = False
            self.__hearbeat_mutex.release
            time.sleep(self.__HEARTBEAT_MONITOR_REFHRES_TIME)

    def __get_time(self) -> int:
        return round(time.time() * 1000)
    
    def is_client_connected(self) -> bool:
        self.__hearbeat_mutex.acquire
        isConnected = self.__isConnected
        self.__hearbeat_mutex.release
        return isConnected

    def wait_for_client(self):
        print("Waiting for client")
        while not self.is_client_connected():
            time.sleep(self.__HEARTBEAT_MONITOR_REFHRES_TIME)
        print("Connected")
