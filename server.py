import socket
import threading
import time 
from axel import Event
import struct

class SocketServer:
    #List with all connected Clients 
    clients = []

    #Constructor 
    def __init__(self, ip = '0.0.0.0', port = 7500):
        self.event = Event()
        self.ip = ip
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.ip, self.port))
        self.serverSocket.listen()

    #start the server
    def run(self):
        print('Server startet')
        try:
            self.acceptClients()
        except Exception as ex:
            print(ex)

    def acceptClients(self):
        while True:
            (clientsocket, address) = self.serverSocket.accept()
            self.clients.append(clientsocket)
            self.onopen(clientsocket)
            t = threading.Thread(target=self.receive, args=(clientsocket,))
            t.daemon = True
            t.start()

    def receive(self, client):
        while True:
            data = client.recv(1024)
            if data:
                self.event(data)
                
    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message)

    def disConnect(self):
        self.serverSocket.close()

    def onopen(self, client):
        print(client)

class MessageMethods:

    def getHeader(byteArray):
        header = byteArray[0:2]
        return int.from_bytes(header, byteorder='little', signed=True), byteArray[2:]

    def getBody(byteArray):
        body = byteArray[2:4]
        return int.from_bytes(body, byteorder='little', signed=True), byteArray[2:]

    def getMessage(byteArray):
        messageLength = byteArray[1]
        message = byteArray[2:messageLength+2]
        return message, byteArray[2+messageLength:]

    def addHeader(byteArray, headerNumber):
        headerNumber = (headerNumber).to_bytes(2, 'little')
        bodyLenght = (len(byteArray)).to_bytes(2, 'little')
        return headerNumber + bodyLenght + byteArray


def onNewMessage(data):
    header, data = MessageMethods.getHeader(data)
    body, data = MessageMethods.getBody(data)
    message, data = MessageMethods.getMessage(data)
    print(header)
    print(body)
    print(message)


if __name__ == "__main__":
    ss = SocketServer()
    t = threading.Thread(target=ss.run)
    t.start()
    ss.event += onNewMessage
    time.sleep(5)
    ss.broadcast(b'Hallo')
    
    #ss.disConnect()