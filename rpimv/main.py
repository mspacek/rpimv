"""On TCP request receipt, grab IMU and magnetometer readings from the
Adafruit LIS3MDL + LSM6DSOX 9 DoF sensor I2C board and return them via TCP.
Also, optionally acquire GPS data from an Adafruit Ultimate GPS USB board.

Install dependencies automatically by running the `setup.py` install script,
or manually with:

$ sudo pip3 install adafruit-circuitpython-lsm6ds
$ sudo pip3 install adafruit-circuitpython-lis3mdl
$ sudo pip3 install adafruit-circuitpython-gps

Execute, optionally specifying port, or host and port:

$ python3 main.py <PORT>
$ python3 main.py <HOST> <PORT>

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
import datetime

import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lis3mdl import LIS3MDL
from adafruit_gps import GPS


# default TCP host to serve on:
#HOST = "localhost" # i.e. 127.0.0.1
# get first IP address returned by `hostname` shell command:
#HOST = subprocess.check_output(['hostname', '-I']).decode().split()[0]
# or just use the DNS name as the host:
HOST = 'rpimv'

# default TCP port to serve on:
PORT = 1987

# default serial port for GPS board:
SERIALPORT = '/dev/ttyUSB0'

# default IMU and magnetometer ranges and data rates:
ACCELRANGE = 2
ACCELDATARATE = 4
GYRORANGE = 0
GYRODATARATE = 4
MAGRANGE = 0
MAGDATARATE = 1


class TCPRequestHandler(socketserver.StreamRequestHandler):
    """Request handler class for TCP server, instantiated once per connection.
    TCP port must be free."""

    def __init__(self, *args, **kwargs):
        i2c = board.I2C() # uses board.SCL and board.SDA
        self.imu = self.init_imu(i2c) # IMU chip instance
        self.mag = self.init_mag(i2c) # magnetometer chip instance
        self.gps = self.init_gps() # GPS board instance
        socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)

    def init_imu(self, i2c):
        """Initialize IMU"""
        imu = LSM6DSOX(i2c)
        imu.accelerometer_range = ACCELRANGE
        imu.accelerometer_data_rate = ACCELDATARATE
        imu.gyro_range = GYRORANGE
        imu.gyro_data_rate = GYRODATARATE
        return imu

    def init_mag(self, i2c):
        """Initialize magnetometer"""
        mag = LIS3MDL(i2c)
        mag.range = MAGRANGE
        mag.data_rate = MAGDATARATE
        return mag

    def init_gps(self):
        """Try and initialize an Adafruit Ultimate GPS USB module instance"""
        gps = None
        try:
            uart = serial.Serial(SERIALPORT, baudrate=9600, timeout=10) # init serial port
            gps = GPS(uart, debug=False) # GPS module instance
            # turn on basic GGA and RMC info:
            gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
            # set update period to 1000 ms, i.e. 1 Hz:
            gps.send_command(b"PMTK220,1000")
            gps.update()
        except Exception as e:
            print(e)
            print('No Adafruit USB GPS device found on port %s' % SERIALPORT)
        return gps

    def handle(self):
        """Override the handle() method to implement communication with client"""
        while True:
            msg = self.rfile.readline().strip().decode()
            dt = datetime.datetime.now()
            print(dt, msg)
            if msg == 'acquire_imu':
                imumag_data = self.get_imumag()
                packet = self.make_imumag_packet(imumag_data)
            elif msg == 'acquire_gps':
                gps_data = self.get_gps()
                packet = self.make_gps_packet(gps_data)
            else:
                packet = "Unknown request %r" % msg
            #print(packet, end='')
            self.wfile.write(packet.encode()) # convert to bytes before writing

    def get_imumag(self):
        """Get current IMU and magnetometer readings"""
        ax, ay, az = self.imu.acceleration # 3 axis acceleration, m/s**2
        wx, wy, wz = self.imu.gyro # 3 axis angular velocity, rad/s
        mx, my, mz = self.mag.magnetic # 3 axis magnetic field strength, uT
        return ax, ay, az, wx, wy, wz, mx, my, mz

    def make_imumag_packet(self, imumag_data):
        """Convert imumag_data to csv byte string"""
        return "%g,%g,%g,%g,%g,%g,%g,%g,%g\n" % imumag_data

    def get_gps(self):
        """Try and get GPS data"""
        gps = self.gps
        if gps is None:
            return 'NO_GPS_BOARD'
        gps.update()
        if not gps.has_fix:
            return 'NO_GPS_FIX'
        lat = gps.latitude # deg
        lon = gps.longitude # deg
        alt = gps.altitude_m or -1 # meters
        #speed = gps.speed_knots # knots
        q = gps.fix_quality # integer, higher numbers -> better quality?
        nsats = gps.satellites or -1
        t = gps.timestamp_utc # time.struct_time, in UTC
        dt = "%04d-%02d-%02d_%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday,
                                                t.tm_hour, t.tm_min, t.tm_sec) # UTC datetime
        return lat, lon, alt, q, nsats, dt

    def make_gps_packet(self, gps_data):
        """Convert imumag_data to csv byte string"""
        if type(gps_data) is str: # just an error message
            return "%s\n" % gps_data
        else:
            return "%g,%g,%g,%d,%d,%s\n" % gps_data


if __name__ == "__main__":
    # create the server, binding to HOST on PORT by default:
    host, port = HOST, PORT # default
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    elif len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    with socketserver.TCPServer((host, port), TCPRequestHandler) as server:
        # start the server - this will continue running until interruped by Ctrl+C
        dt = datetime.datetime.now()
        print(dt, 'Serving on %s:%d, Ctrl+C to cancel ...' % (host, port))
        server.serve_forever()
