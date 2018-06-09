import random
import time
import socket
import sys
import threading
import Queue
import math
from collections import deque
import csv

class Sender:

    s = None
    HOST = ''
    port = 0
    lock = None
    packetSize = 1000
    delay = 1
    isPeriodicallySending = False
    q = None

    # host and port specify the server to connect to. packetSize specifies
    # the constant packet size, while delay specifies the constant
    # interpacket delay.
    def __init__(self, host, port, packetSize, delay):
        Sender.HOST = host    # The remote host
        Sender.PORT = port    # The same port as used by the server

        # open the socket
        for res in socket.getaddrinfo(Sender.HOST, Sender.PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                Sender.s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                Sender.s = None
                continue
            try:
                Sender.s.connect(sa)
            except socket.error as msg:
                Sender.s.close()
                Sender.s = None
                continue
            break
        if Sender.s is None:
            print 'could not open socket'
            sys.exit(1)

        # initialize parameters
        Sender.lock = threading.Lock()
        Sender.isPeriodicallySending = False
        Sender.packetSize = packetSize
        Sender.delay = delay
        Sender.q = Queue.Queue();

    # This function is called by the device when it needs to
    # send out information
    def send(self, msg):
        Sender.lock.acquire()
        try:
            Sender.q.put(msg)
        finally:
            Sender.lock.release()

    def __sendHelper__(self):
        while (Sender.isPeriodicallySending):
            time.sleep(Sender.delay)
            self.__sendPeriodicMessage__()            

    def __sendPeriodicMessage__(self):
        Sender.lock.acquire()
        length = Sender.packetSize

        try:
            # if there is real traffic to be sent, send it
            if not Sender.q.empty():
                msgOrigLength = len(Sender.q.queue[0])
                finalMessage = ''
                header = '1'
                if msgOrigLength <= length:
                    msg = Sender.q.get()
                    content = ''.join(['\00' for x in range(length - msgOrigLength)])
                    header = header + '1' + str(len(msg)) + ';'
                    finalMessage = msg + content
                else:
                    header = header + '0' + str(length) + ';'
                    finalMessage = Sender.q.queue[0][0:length]
                    newFirstElement = Sender.q.queue[0][length:]
                    Sender.q.queue[0] = newFirstElement
                Sender.s.sendall(header + finalMessage)
            # otherwise, send cover traffic
            else:
                header = '00'
                header = header + str(length) + ';'
                finalMessage = ''.join(['\00' for x in range(length)])
                Sender.s.sendall(header + finalMessage)
        finally:
            Sender.lock.release()

    # This function is called before the device starts sending any
    # information.
    def startPeriodicallySending(self):
        Sender.isPeriodicallySending = True
        t = threading.Thread(target=self.__sendHelper__)
        t.start()

    # This function is called to stop periodic sending
    def close(self):
        Sender.isPeriodicallySending = False
        while not Sender.q.empty():
            time.sleep(Sender.delay)
            self.__sendPeriodicMessage__()
        time.sleep(3 * Sender.delay)
        Sender.s.close()

def main():
    sender = Sender("10.0.0.111", 3490, 150, 0.05)
    time.sleep(1)
    sender.startPeriodicallySending()
    i = 0
    currentTime = 0
    with open('abbrlowlat.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if i == 0:
                i += 1
                currentTime = float(row[0])
                sender.send(row[1])
            else:
                newTime = float(row[0])
                time.sleep(newTime - currentTime)
                sender.send(row[1])
                currentTime = newTime
                print i
                i += 1
    time.sleep(3)
    sender.close()

#main()






