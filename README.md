# MCP4725

Example code extended from: [Wayoda](https://github.com/wayoda/micropython-mcp4725)

Depending on the device, connect the I2C wires to the board (or use the Qwiic cable). Use `i2c.scan()` to check if the device is connected and returns with the correct address (0x60 or 0x62).

```python
import mcp4725
import time
from machine import I2C

if __name__ == "__main__":
    # device connected on Pin0 and 1 (else use different pin-numbers)
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
    # the Adafruit Qwiic connecter board has default address 0x62
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

If you want to check if the sensor is working you can connect the output to the Raspberry Pi Pico ADC. With the help of [threading](https://github.com/ddland/micropython/tree/main/tips/threading). As an example, to have continiuous readings from the ADC on the Raspberry Pi Pico while changing the MCP4725 DAC you can use adapt the following example:

```python 
import mcp4725
import machine
import time
import _thread

class Sensor:
    """ Class for the ADC sensor
    Once running, will print the measured values from the ADC channel.
    """
    
    nthreads = 0
    running = False
    
    def __init__(self, ADC=0, dt=1):
        """ Sensor class initializing

        arguments: ADC: ADC number from the Pico Pi (0,1,2,3)
                   dt: delay between prints from the ADC
        """
        self.dt = dt
        self.adc = machine.ADC(ADC)
        
    def start(self):
        if self.nthreads > 0:
            return
        self.nthreads = 1
        _thread.start_new_thread(self.run, ())
        
    def run(self):
        self.running = True
        while self.running:
            print(3.3*self.adc.read_u16()/(2**16-1))
            time.sleep(self.dt)
            
    def stop(self):
        self.running = False
    
        

if __name__ == "__main__":
    # mcp4725 device connected on Pin0 and 1 (else use different pin-numbers)
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
    # the Adafruit Qwiic connecter has default address 0x62
    mcp = mcp4725.MCP4725(i2c, address=0x62, debug=False)
    
    # start the ADC measurement on ADC=0 with a delay of 0.5 seconds per reading
    sensor = Sensor(ADC=0, dt=0.5)
    sensor.start()

    # Go in 10 devisions trough the MCP4725 range
    N = 10.0
    step = (2**12-1)/N
    
    for ii in range(N+1):  #+1 to inlude the upper boundary
        mcp.write(ii*step) #change the output to the next value
        time.sleep(1)      # wait for 3 seconds to get some datavalues
    mcp.write(0)           # return to zero...
    time.sleep(1)
    sensor.stop()          # stop the sensor thread.
```

Where the sensor class wraps the ADC in a new thread and lets it print every dt-delay the reading.

