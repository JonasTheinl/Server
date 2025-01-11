import socket
import threading
import time
from axel import Event
import select

class SocketServer:
    clients = set() 

    def __init__(self, ip='0.0.0.0', port=7500):
        self.event = Event()
        self.ip = ip
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.ip, self.port))
        self.serverSocket.listen()
        self.checkThread = threading.Thread(target=self.checkConnection)
        self.checkThread.start()

    def run(self):
        print('Server startet')
        try:
            self.acceptClients()
        except Exception as ex:
            print(ex)

    def acceptClients(self):
        while True:
            (clientsocket, address) = self.serverSocket.accept()
            self.clients.add(clientsocket)  
            self.onopen(clientsocket)
            t = threading.Thread(target=self.receive, args=(clientsocket,))
            t.daemon = True
            t.start()

    def receive(self, client):
        while True:
            try:
                data = client.recv(1024)
                if data:
                    self.event(data)
                else:  
                    self.clients.remove(client)
                    break
            except socket.error:
                self.clients.remove(client)
                break

    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message)

    def disConnect(self):
        self.serverSocket.close()
        self.clients.clear()  

    def onopen(self, client):
        print(client)

    def checkConnection(self):
        while True:
            remove_clients = []  
            for client in self.clients:
                ready = select.select([client], [], [], 1)  
                if ready[0]:
                    try:
                        data = client.recv(1024)  
                        if not data:
                            remove_clients.append(client)
                    except socket.error:
                        remove_clients.append(client)
            for client in remove_clients:
                self.clients.remove(client)
            time.sleep(5)  



