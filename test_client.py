"""A client to test the server, polls the server at regular intervals.

see:

https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example
"""

import sys
import time
import socket

HOST, PORT = "localhost", 9999
POLLINTERVAL = 1.0 # s

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, port))
        while True:
            #sock.sendall(bytes(data + "\n", "utf-8"))
            sock.sendall(b'acquire')

            # Receive data from the server and shut down
            data = str(sock.recv(1024), "utf-8")
            print(data)

            time.sleep(POLLINTERVAL)
