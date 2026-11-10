#!/usr/bin/env python3
"""Write a 320x240 RGB565 frame to the X24 ST7789V2 LCD."""
import fcntl
import os
from pathlib import Path
import struct
import time

frame=Path('/usr/local/share/vis-display/hello-world.rgb565').read_bytes()
assert len(frame)==320*240*2
assert Path('/sys/class/gpio/gpiochip515/label').read_text().strip()=='4201000.gpio'

def gpio(number):
    path=Path('/sys/class/gpio')/('gpio'+str(number))
    if not path.exists():
        Path('/sys/class/gpio/export').write_text(str(number))
    (path/'direction').write_text('high')
    return path/'value'

reset=gpio(516) # Verdin GPIO_1, LCD and touch reset
dc=gpio(517)    # Verdin GPIO_2, LCD command/data
fd=os.open('/dev/spidev0.0',os.O_WRONLY)
try:
    fcntl.ioctl(fd,0x40016b01,struct.pack('B',0)) # SPI mode 0
    fcntl.ioctl(fd,0x40016b03,struct.pack('B',8))
    fcntl.ioctl(fd,0x40046b04,struct.pack('I',500000))
    def write(data):
        for start in range(0,len(data),4096):
            chunk=data[start:start+4096]
            if os.write(fd,chunk)!=len(chunk):
                raise IOError('Short SPI write')
    def cmd(code,data=b''):
        dc.write_text('0');write(bytes([code]))
        if data:
            dc.write_text('1');write(bytes(data))
    reset.write_text('0');time.sleep(.05)
    reset.write_text('1');time.sleep(.15)
    cmd(0x01);time.sleep(.15)       # software reset
    cmd(0x11);time.sleep(.12)       # sleep out
    cmd(0x3a,[0x55])               # RGB565
    cmd(0x36,[0x60])               # landscape: swap rows/columns
    cmd(0x13);time.sleep(.01)      # normal display mode
    cmd(0x2a,[0,0,1,0x3f])         # columns 0..319
    cmd(0x2b,[0,0,0,0xef])         # rows 0..239
    cmd(0x2c)
    dc.write_text('1');write(frame)
    cmd(0x29);time.sleep(.1)       # display on
    print('Sent Hello World frame to ST7789V2 at 500 kHz; awaiting visual confirmation.')
finally:
    os.close(fd)
