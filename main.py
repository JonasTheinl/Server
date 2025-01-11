from SocketServer import SocketServer
import threading
from axel import Event


def onNewMessage(data):
    print(data)

def main():
    ss = SocketServer()
    t = threading.Thread(target=ss.run)
    t.start()
    ss.event += onNewMessage


if __name__ == "__main__":
    main()