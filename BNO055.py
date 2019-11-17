import smbus

# Default I2C Address of the device
ADDRESS = 0x28

# Addresses of setting registers


class BNO055:
    """ Setups and reads data from the BNO055 9 degree of freedom sensor. """

    def __init__(self, bus, address=ADDRESS):

        self.bus = smbus.SMBus(bus)
        self.address = address