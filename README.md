A Python server for Raspberry Pi that serves IMU data over TCP.
Uses Adafruit LIS3MDL + LSM6DSOX 9 DoF sensor I2C board.

See:

https://learn.adafruit.com/st-9-dof-combo/python-circuitpython

Server side:

```
$ python3 main.py
Serving on 192.168.178.39:9999 ...
acquire
acquire
acquire
acquire
```

Client side:

```
$ python3 test_client.py
Connected to rpimv:9999 ...
-3.30688,-0.184247,9.4349,-0.00610865,-0.00702495,-0.000305433,15.9456,7.79012,2.3385
-3.29731,-0.17348,9.45165,-0.00641409,-0.0267254,-0.000763582,16.1502,7.98012,2.28004
-3.30329,-0.184247,9.43969,-0.00549779,-0.00641409,-0.000610865,15.8433,7.90704,2.41158
-3.31406,-0.180658,9.43251,-0.00626137,-0.00763582,-0.000763582,15.6825,8.17013,2.67466
```
