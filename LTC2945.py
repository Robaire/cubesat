import smbus

# Default I2C Address of the device
ADDRESS = 0x67

# Addresses of setting registers
CONTROL = 0x00
ALERT = 0x01


class LTC2945:
    """ Sets up and reads data from the LTC2945 ADC. """

    def __init__(self, bus, address=ADDRESS):

        self.bus = smbus.SMBus(bus)
        self.address = address

        # Set sensor settings
        self.bus.write_byte_data(self.address, CONTROL, 0b00000100)
        self.bus.write_byte_data(self.address, ALERT, 0b00000000)

    def read_voltage(self):
        """ Read the voltage of the sense pin. """
        data = self.bus.read_i2c_block_data(self.address, 0x28, 2)
        volt = int.from_bytes(data[0:2], byteorder='big', signed=True)
        print(data)
        print(volt)
        return volt

    def read(self):
        print(self.bus.read_i2c_block_data(self.address, 0x00, 1))


class Dummy:
    def __init__(self):
        pass

    def read_voltage(self):
        print(15)
        return 15.0