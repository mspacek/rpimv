"""On TCP request receipt, grab IMU and magnetometer readings from the
Adafruit LIS3MDL + LSM6DSOX 9 DoF sensor I2C board and return them via TCP.

Install required dependencies with:

```
sudo pip3 install adafruit-circuitpython-lsm6ds
sudo pip3 install adafruit-circuitpython-lis3mdl
```

Execute, optionally specifying host port:

```
python3 main.py <PORT>
```

see:

https://learn.adafruit.com/st-9-dof-combo/python-circuitpython
https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS
https://github.com/adafruit/Adafruit_CircuitPython_LIS3MDL

https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example
"""

import sys
import subprocess
import socketserver

import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lis3mdl import LIS3MDL

#host = "localhost"
# get first IP address returned by `hostname` shell command:
host = subprocess.check_output(['hostname', '-I']).decode().split()[0]
# or just use the DNS name as the host:
#host = 'rpimv'

PORT = 1987


class TCPRequestHandler(socketserver.StreamRequestHandler):
    """Request handler class for TCP server, instantiated once per connection
    and port must be free"""

    def __init__(self, *args, **kwargs):
        i2c = board.I2C() # uses board.SCL and board.SDA
        self.imu = LSM6DSOX(i2c) # IMU chip
        self.mag = LIS3MDL(i2c)
        socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        """Override the handle() method to implement communication with client"""
        # self.request is the TCP socket connected to the client
        #msg = self.request.recv(1024).strip().decode() # from bytes to str
        # Alternatively, self.rfile is a file-like object created by the handler
        # that uses readline() instead of raw recv() calls:
        while True:
            msg = self.rfile.readline().strip().decode()
            #print("{} wrote:".format(self.client_address[0]))
            print(msg)
            if msg == 'acquire':
                #print('got acquire message')
                imumag_data = self.get_imumag()
                #gpsdata = get_gps()
                data_packet = self.make_packet(imumag_data)
                #print(data_packet)
                #self.request.sendall(data_packet)
                # Likewise, self.wfile is a file-like object to write back
                # to the client instead of raw sendall() calls:
                self.wfile.write(data_packet)

    def get_imumag(self):
        ax, ay, az = self.imu.acceleration # m/s**2
        rx, ry, rz = self.imu.gyro # rad/s
        mx, my, mz = self.mag.magnetic # uT
        return ax, ay, az, rx, ry, rz, mx, my, mz
    '''
    def get_gps(self):
        ## TODO
        pass
    '''
    def make_packet(self, imumag_data):
        """Convert imumag_data to csv string"""
        return b"%g,%g,%g,%g,%g,%g,%g,%g,%g\n" % imumag_data


if __name__ == "__main__":
    # Create the server, binding to host on PORT:
    port = PORT # default
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    with socketserver.TCPServer((host, port), TCPRequestHandler) as server:
        # Start the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print('Serving on %s:%s ...' % (host, port))
        server.serve_forever()
