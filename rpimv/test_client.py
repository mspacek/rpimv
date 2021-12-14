"""A client to test the server, polls the server at regular intervals.

see:

https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example

Execute, optionally specifying port, or host and port:

```
python3 test_client.py <PORT>
python3 test_client.py <HOST> <PORT>
```

"""

import sys
import time
import socket

# default TCP host and port to connect to:
HOST, PORT = 'rpimv', 1987
#HOST, PORT = '192.168.178.40', 1987
POLLINTERVAL = 1.0 # s

if __name__ == "__main__":
    host, port = HOST, PORT
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    elif len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    # Create a socket (SOCK_STREAM means a TCP socket):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data:
        sock.connect((host, port))
        print("Connected to %s:%d, Ctrl+C to cancel ..." % (host, port))
        while True: # keep the socket open indefinitely
            sock.sendall(b'acquire_imu\n') # send IMU acquire request
            imu_data = str(sock.recv(1024), "utf-8").strip() # receive data from server
            print(imu_data)
            sock.sendall(b'acquire_gps\n') # send GPS acquire request
            gps_data = str(sock.recv(1024), "utf-8").strip() # receive data from server
            print(gps_data)
            time.sleep(POLLINTERVAL)
