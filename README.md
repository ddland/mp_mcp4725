# MCP4725

Example code extended from: 
[https://github.com/wayoda/micropython-mcp4725](Wayoda)

Depending on the device, connect the I2C wires to the board (or use the Qwiic cable). 

```python
import mcp4725
import time
from machine import I2C

if __name__ == "__main__":
    # device connected on Pin0 and 1 (else use different pin-numbers)
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
    # the Adafruit Qwiic connecter has default address 0x62
    mcp = mcp4725.MCP4725(i2c, address=0x62)

    # with a 12 bit DAC the maximum value (corresponding on a 3.3V device
    # is 2**12-1.
    # scale is from 0 till 2**12, where each step is 3.3/(2**12-1) V.
    mcp.write(2**11) # set the device to a high value, should be close to
                     #3.3V * (2**11/(2**12-1) = 1.65V) 
    print("Should be 1.65V on the out-pins!")
    time.sleep(10)
    mcp.write(2**4)  # 0.0129 V on the 3.3V picopi
    print("Should be 0.0129V on the out-pins!")
```
