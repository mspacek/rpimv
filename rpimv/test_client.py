"""A client to test the server, polls the server at regular intervals.

see:

https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example

Execute, optionally specifying host port:

```
python3 test_client.py <PORT>
```

"""

import sys
import time
import socket

#HOST, PORT = 'rpimv', 1987
HOST, PORT = '192.168.178.40', 1987
POLLINTERVAL = 1.0 # s

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    # Create a socket (SOCK_STREAM means a TCP socket):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data:
        sock.connect((HOST, port))
        print("Connected to %s:%s ..." % (HOST, port))
        while True: # keep the socket open indefinitely
            sock.sendall(b'acquire_imu\n') # send acquire request
            imu_data = str(sock.recv(1024), "utf-8").strip() # receive data from server
            print(imu_data)
            sock.sendall(b'acquire_gps\n') # send acquire request
            gps_data = str(sock.recv(1024), "utf-8").strip() # receive data from server
            print(gps_data)
            time.sleep(POLLINTERVAL)
