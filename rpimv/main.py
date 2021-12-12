"""On TCP request receipt, grab IMU and magnetometer readings from the
Adafruit LIS3MDL + LSM6DSOX 9 DoF sensor I2C board and return them via TCP.
Also, optionally acquire GPS data from an Adafruit Ultimate GPS USB board.

Install required dependencies with:

```
sudo pip3 install adafruit-circuitpython-lsm6ds
sudo pip3 install adafruit-circuitpython-lis3mdl
sudo pip3 install adafruit-circuitpython-gps
```

Execute, optionally specifying host port:

```
python3 main.py <PORT>
```

see:

https://learn.adafruit.com/st-9-dof-combo/python-circuitpython
https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS
https://github.com/adafruit/Adafruit_CircuitPython_LIS3MDL
https://github.com/adafruit/Adafruit_CircuitPython_GPS

https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example
"""

import sys
import subprocess
import socketserver
import serial

import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lis3mdl import LIS3MDL
from adafruit_gps import GPS


# TCP globals:
#HOST = "localhost"
# get first IP address returned by `hostname` shell command:
HOST = subprocess.check_output(['hostname', '-I']).decode().split()[0]
# or just use the DNS name as the host:
#HOST = 'rpimv'
PORT = 1987
# GPS globals:
SERIALPORT = '/dev/ttyUSB0'



class TCPRequestHandler(socketserver.StreamRequestHandler):
    """Request handler class for TCP server, instantiated once per connection.
    TCP port must be free."""

    def __init__(self, *args, **kwargs):
        i2c = board.I2C() # uses board.SCL and board.SDA
        self.imu = LSM6DSOX(i2c) # IMU chip instance
        self.mag = LIS3MDL(i2c) # magnetometer chip instance
        self.init_gps()

        socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)

    def init_gps(self):
        """Try and initialize an Adafruit Ultimate GPS USB module instance"""
        self.gps = None
        try:
            uart = serial.Serial(SERIALPORT, baudrate=9600, timeout=10) # init serial port
            self.gps = adafruit_gps.GPS(uart, debug=False) # GPS module instance
            # turn on basic GGA and RMC info:
            self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
            # set update period to 1000 ms, i.e. 1 Hz:
            self.gps.send_command(b"PMTK220,1000")
            self.gps.update()
        except:
            print('No Adafruit USB GPS device found on port %s' % SERIALPORT)
            pass

    def handle(self):
        """Override the handle() method to implement communication with client"""
        while True:
            msg = self.rfile.readline().strip().decode()
            print(msg)
            if msg == 'acquire_imu':
                imumag_data = self.get_imumag()
                packet = self.make_imumag_packet(imumag_data)
            elif msg == 'acquire_gps':
                gps_data = self.get_gps()
                packet = self.make_gps_packet(gps_data)
            else:
                packet = b"Unknown request %r" % msg
            #print(packet.decode())
            self.wfile.write(packet)

    def get_imumag(self):
        """Get current IMU and magnetometer readings"""
        ax, ay, az = self.imu.acceleration # m/s**2
        rx, ry, rz = self.imu.gyro # rad/s
        mx, my, mz = self.mag.magnetic # uT
        return ax, ay, az, rx, ry, rz, mx, my, mz

    def make_imumag_packet(self, imumag_data):
        """Convert imumag_data to csv byte string"""
        return b"%g,%g,%g,%g,%g,%g,%g,%g,%g\n" % imumag_data

    def get_gps(self):
        """Try and get GPS data"""
        if self.gps is None:
            return 'NOGPS'
        self.gps.update()
        if not self.gps.has_fix:
            return 'NOFIX'
        lat = self.gps.latitude # deg
        lon = self.gps.longitude # deg
        alt = gps.altitude_m # meters
        speed = gps.speed_knots # knots
        q = gps.fix_quality # integer, higher numbers -> better quality?
        nsats = gps.satellites
        t = gps.timestamp_utc # time.struct_time
        dt = "%04d-%02d-%02d_%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday,
                                                t.tm_hour, t.tm_min, t.tm_sec) # ISO datetime
        return lat, lon, alt, speed, q, nsats, dt

    def make_gps_packet(self, gps_data):
        """Convert imumag_data to csv byte string"""
        if type(gps_data) is str: # just an error message
            return b"%s\n" % gps_data
        else:
            return b"%g,%g,%g,%g,%d,%d,%s\n" % gps_data


if __name__ == "__main__":
    # create the server, binding to HOST on PORT by default:
    host, port = HOST, PORT # default
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    elif len(sys.argv) == 3:
        host, port = int(sys.argv[1]), int(sys.argv[2])
    with socketserver.TCPServer((host, port), TCPRequestHandler) as server:
        # start the server - this will continue running until interruped by Ctrl+C
        print('Serving on %s:%s ...' % (host, port))
        server.serve_forever()
