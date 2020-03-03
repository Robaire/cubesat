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
        self.bus.write_byte_data(self.address, CONTROL, 0b00000101)
        self.bus.write_byte_data(self.address, ALERT, 0b00000000)

    def read_voltage(self):
        """ Read the voltage of the sense pin. """
        data = self.bus.read_i2c_block_data(self.address, 0x28, 2)
        volt = int.from_bytes(data[0:2], byteorder='big', signed=True)
        print(data)
        print(volt)
        return volt

    def read(self):
        # print(self.bus.read_i2c_block_data(self.address, 0x00, 1))
        # print(self.bus.read_i2c_block_data(self.address, 0x05, 3))
        # print(self.bus.read_i2c_block_data(self.address, 0x14, 2))
        # print(self.bus.read_i2c_block_data(self.address, 0x1E, 2))
        # print(self.bus.read_i2c_block_data(self.address, 0x28, 2))

        power = self.bus.read_i2c_block_data(self.address, 0x05, 3)
        sense = self.bus.read_i2c_block_data(self.address, 0x14, 2)
        vin = self.bus.read_i2c_block_data(self.address, 0x1E, 2)

        p_power = int.from_bytes(power, byteorder='big', signed=False)
        v_sense = int.from_bytes(sense, byteorder='big', signed=False) >> 4
        v_vin = int.from_bytes(vin, byteorder='big', signed=False) >> 4

        print("Power: " + str(p_power))
        print("V Sense: " + str(v_sense))
        print("V In:" + str(v_vin))

class Dummy:
    def __init__(self):
        pass

    def read_voltage(self):
        print(15)
        return 15.0