# Echo server program
import time
import socket
import sys

# This function is used to process messages on the
# receiving end. s is a socket and conn is the
# connection returned by accept()
def recv(s, conn):
    string = ''
    while 1:
        data = conn.recv(1024)
        if not data: break
        if data[0] == '1':
            split = data[2:].split(';', 1)
            length = int(split[0])
            string = string + split[1][0:length]
            if data[1] == '1':
                return string
    return None



    
def main():
    HOST = "10.0.0.111"              
    PORT = 3490             
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(1)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print 'could not open socket'
        sys.exit(1)
    while (1):
        print "accepting..."
        conn, addr = s.accept()
        print 'Connected by', addr
        while 1:
            message = recv(s, conn)
            if message == None:
                break
        conn.close()

main()

