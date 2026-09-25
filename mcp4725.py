#https://raw.githubusercontent.com/wayoda/micropython-mcp4725/master/mcp4725.py
#Library for the MCP4725 I2C bus DAC 

#The device supports a few power down modes on startup and during operation 
POWER_DOWN_MODE = {'Off':0, '1k':1, '100k':2, '500k':3}
        
class MCP4725:
    bus_addresses = [0x60, 0x62]
    
    def __init__(self,i2c, address=0x60) :
        self.i2c=i2c
        self.address=address
        self.scan()
        self._writeBuffer=bytearray(2)
        
    def scan(self):
        i2cscan = self.i2c.scan()
        if self.address not in i2cscan:
            print("MCP4725 device not detected. Is the right address provided?")
            print("Detected addresses on I2C bus:")
            print(i2cscan)
            print(f"Provided address: {self.address}")
            raise Exception("MCP4725 device not found on bus!")
            
    def write(self,value):
        if value < 0:
            value=0
        value=value & 0xFFF
        self._writeBuffer[0]=(value>>8) & 0xFF
        self._writeBuffer[1]=value & 0xFF
        return self.i2c.writeto(self.address,self._writeBuffer)==2

    def read(self):
        buf=bytearray(5)
        if self.i2c.readfrom_into(self.address,buf) ==5:
            eeprom_write_busy=(buf[0] & 0x80)==0
            power_down=self._powerDownKey((buf[0] >> 1) & 0x03)
            value=((buf[1]<<8) | (buf[2])) >> 4
            eeprom_power_down=self._powerDownKey((buf[3]>>5) & 0x03)
            eeprom_value=((buf[3] & 0x0f)<<8) | buf[4] 
            return (eeprom_write_busy,power_down,value,eeprom_power_down,eeprom_value)
        return None

    def config(self,power_down='Off',value=0,eeprom=False):
        buf=bytearray()
        conf=0x40 | (POWER_DOWN_MODE[power_down] << 1)
        if eeprom:
            #store the powerdown and output value in eeprom
            conf=conf | 0x60
        buf.append(conf)
        #check value range
        if value<0:
            value=0
        value=value & 0xFFF
        buf.append(value >> 4)
        buf.append((value & 0x0F)<<4)
        return self.i2c.writeto(self.address,buf)==3

    def _powerDownKey(self,value):
        for key,item in POWER_DOWN_MODE.items():
            if item == value:
                return key
                
if __name__ == "__main__":
    from machine import I2C
    import time
    sda = machine.Pin(0)
    scl = machine.Pin(1)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
    mcp = MCP4725(i2c, address=0x60)
    mcp.write(2**11) # 12 bit number, 2**12-1 maximal
    time.sleep(10)
    mcp.write(2**4)
    time.sleep(5)
    mcp.write(2**8)
