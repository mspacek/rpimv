A Python server for Raspberry Pi that serves IMU data over TCP.
Uses Adafruit LIS3MDL + LSM6DSOX 9 DoF sensor I2C board. Also
optionally serves GPS data from an Adafruit Ultimate GPS USB board.

See:

https://learn.adafruit.com/st-9-dof-combo
https://learn.adafruit.com/adafruit-ultimate-gps

To install in developer mode, including dependencies:

```
$ sudo pip3 install -e .
```

To run the server:

```
$ python3 rpimv/main.py
Serving on rpimv:1987 ...
2021-12-12 12:00:00.000000 acquire_imu
2021-12-12 12:00:00.000000 acquire_gps
2021-12-12 12:00:01.000000 acquire_imu
2021-12-12 12:00:01.000000 acquire_gps
```

or simply run the installed `rpimv` script from anywhere.

To test the server with a simple client:

```
$ python3 rpimv/test_client.py
Connected to rpimv:1987 ...
-3.30688,-0.184247,9.4349,-0.00610865,-0.00702495,-0.000305433,15.9456,7.79012,2.3385
NO_GPS_FIX
-3.29731,-0.17348,9.45165,-0.00641409,-0.0267254,-0.000763582,16.1502,7.98012,2.28004
NO_GPS_FIX
```
