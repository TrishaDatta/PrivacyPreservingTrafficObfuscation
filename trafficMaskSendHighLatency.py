import random
import time
import socket
import sys
import threading
import Queue
import csv
class Sender:

    s = None
    HOST = ''
    port = 0
    lock = None
    UNIFORM_DIST = 0
    NORMAL_DIST = 1
    dist = UNIFORM_DIST
    param1 = 0
    param2 = 1
    packetSizeLow = 0
    packetSizeHigh = 1024
    isPeriodicallySending = False
    q = None
    
    # host and port specify the server to connect to. dist must be either
    # Sender.UNIFORM_DIST (default) or Sender.NORMAL_DIST; this specifies
    # the type of distribution for packet sizes. [param1, param2] specifies
    # the interval from which interpacket delays are drawn. If dist is
    # Sender.UNIFORM_DIST, then packet sizes are drawn uniformly from the 
    # interval [packetSizeLow, packetSizeHigh]. Otherwise, packet sizes
    # are drawn from a Gaussian distribution with mean packetSizeLow and
    # variance packetSizeHigh.
    def __init__(self, host, port, dist, param1, param2, packetSizeLow, packetSizeHigh):
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
        Sender.dist = dist
        Sender.param1 = param1
        Sender.param2 = param2
        Sender.q = Queue.Queue();
        Sender.lock = threading.Lock()
        Sender.isPeriodicallySending = False
        Sender.packetSizeLow = packetSizeLow
        Sender.packetSizeHigh = packetSizeHigh

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
            delay = random.uniform(Sender.param1, Sender.param2)
            time.sleep(delay)
            self.__sendPeriodicMessage__()


    def __sendPeriodicMessage__(self):
        Sender.lock.acquire()

        # randomly set the length of the next packet to be sent
        length = 0
        if Sender.dist == Sender.UNIFORM_DIST:
            length = random.randint(Sender.packetSizeLow, Sender.packetSizeHigh)
        else:
            length = int(random.gauss(Sender.packetSizeLow, Sender.packetSizeHigh))

        
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
            delay = random.uniform(Sender.param1, Sender.param2)
            time.sleep(delay)
            self.__sendPeriodicMessage__()
        Sender.s.close()

def main():
    sender = Sender("10.0.0.111", 3490, Sender.UNIFORM_DIST, 0.2, 0.4, 50, 200)
    time.sleep(1)
    sender.startPeriodicallySending()
    i = 0
    currentTime = 0
    with open('abbr.csv', 'rb') as csvfile:
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
    sender.close()

main()



