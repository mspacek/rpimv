"""rpimv installation script

A "developer" install lets you work on or otherwise update rpimv in-place, in whatever
folder you cloned it into with git, while still being able to call `import rpimv` and use it
as a library system-wide. This creates an egg-link in your system site-packages or
dist-packages folder to the source code:

$ sudo python setup.py develop

or the equivalent using pip:

$ sudo pip3 install -e .

This will also install a bash script on your system so that you can simply type `rpimv` at the
command line to launch it from anywhere.
"""


from setuptools import setup
from rpimv.__version__ import __version__

setup(name='rpimv',
      version=__version__,
      license='BSD',
      description="A Python server for Raspberry Pi that serves IMU data over TCP",
      author='Martin Spacek',
      author_email='git at mspacek mm st',
      url='https://github.com/mspacek/rpimv',
      # include subfolders with code as additional packages
      packages=['rpimv'],
      scripts=['bin/rpimv'],
      install_requires=['adafruit-circuitpython-lsm6ds',
                        'adafruit-circuitpython-lis3mdl',
                        'adafruit-circuitpython-gps'
                        ]
      )
