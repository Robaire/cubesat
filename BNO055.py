import time
import smbus

# Default I2C Address of the device
ADDRESS = 0x28

# Addresses of setting registers
ST_RESULT = 0x36  # Contains the result of the startup self check
OPR_MODE = 0x3d
UNIT_SEL = 0x3b

ACC_CONFIG = 0x08
MAG_CONFIG = 0x09
GYR_CONFIG = 0x0a

# Starting addresses of data registers
TEMP = 0x33
ACC_DATA = 0x08
GYR_DATA = 0x14
MAG_DATA = 0x0e

class BNO055:
    """ Setups and reads data from the BNO055 9 degree of freedom sensor. """

    def __init__(self, bus, address=ADDRESS):

        self.bus = smbus.SMBus(bus)
        self.address = address

        # Set sensor settings
        self.bus.write_byte_data(self.address, ACC_CONFIG, 0b00001100)  # 2g, 62.5Hz
        self.bus.write_byte_data(self.address, MAG_CONFIG, 0b00011011)  # High Accuracy, 10Hz
        self.bus.write_byte_data(self.address, GYR_CONFIG, 0b00001011)  # 250dps, 230Hz

        # Set units for all sensors
        self.bus.write_byte_data(self.address, UNIT_SEL, 0b10000000)  # Degrees, m/s^2, C

        # Enter operating mode
        time.sleep(0.05)
        self.bus.write_byte_data(self.address, OPR_MODE, 0b0111)

    @staticmethod
    def parse_axis(data, scale):
        """ Splits sensor data into component axis, combining MSB and LSB. """
        print(data)
        x = int.from_bytes(data[0:2], byteorder='little', signed=True) / scale
        y = int.from_bytes(data[2:4], byteorder='little', signed=True) / scale
        z = int.from_bytes(data[4:6], byteorder='little', signed=True) / scale
        return x, y, z

    def read_accel(self):
        """ Read data from the accelerometer. """
        data = self.bus.read_i2c_block_data(self.address, ACC_DATA, 6)
        return self.parse_axis(data, 100)

    def read_gyro(self):
        """ Read data from the gyroscope. """
        data = self.bus.read_i2c_block_data(self.address, GYR_DATA, 6)
        return self.parse_axis(data, 16)

    def read_mag(self):
        """ Read data from the magnetometer. """
        data = self.bus.read_i2c_block_data(self.address, MAG_DATA, 6)
        return self.parse_axis(data, 16)

    def read_temp(self):
        """ Read data from the temperature sensor. """
        temp = self.bus.read_byte_data(self.address, TEMP)
        return temp
