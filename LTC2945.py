import smbus
import random

# Default I2C Address of the device
ADDRESS = 0x67

# Value of the sense resistor in ohms
SENSE = 0.02

class LTC2945:
    """ Sets up and reads data from the LTC2945 ADC. """

    def __init__(self, bus, address=ADDRESS):

        self.bus = smbus.SMBus(bus)
        self.address = address

        # Set sensor settings
        self.bus.write_byte_data(self.address, 0x00, 0b00000101)
        self.bus.write_byte_data(self.address, 0x01, 0b00000000)

    def read_sense(self):
        """ Returns the voltage drop across the sense resistor in volts."""

        # Read the Vsense registers
        data = self.bus.read_i2c_block_data(self.address, 0x14, 2)

        # Due to the way the values are stored on the LTC2945 the result must be bit shifted
        sense = int.from_bytes(data, byteorder='big', signed=False) >> 4

        # Multiple my 25uV to get the output in volts
        return sense * 0.000025

    def read_vin(self):
        """ Returns the voltage at the input pin in volts. """

        # Read the Vin registers
        data = self.bus.read_i2c_block_data(self.address, 0x1E, 2)

        # Due to the way the values are stored on the LTC2945 the result must be bit shifted
        vin = int.from_bytes(data, byteorder='big', signed=False) >> 4

        # Multiple by 25mV to get the output in volts
        return vin * 0.025

    def read_current(self):
        """ Returns the current measured across the sense resistor in amps. """

        # V = I*R
        return self.read_sense() / SENSE

    def read_power(self):
        """ Returns the current power consumption in watts. """

        # W = V*A
        return self.read_current() * self.read_vin()


class Dummy:
    def __init__(self):
        pass

    def read_sense(self):
        """ Returns the voltage drop across the sense resistor in volts."""
        return random.random()

    def read_vin(self):
        """ Returns the voltage at the input pin in volts. """
        return 15 + random.random() * 0.8

    def read_current(self):
        """ Returns the current measured across the sense resistor in amps. """
        return random.random() * 1.8 + 0.5

    def read_power(self):
        """ Returns the current power consumption in watts. """
        return self.read_current() * self.read_vin()