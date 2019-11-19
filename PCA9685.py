import smbus

# Default I2C Address of the device
ADDRESS = 0x40

# Addresses of setting registers
MODE1 = 0x00
MODE2 = 0x01
PRE_SCALE = 0xfe

# Addresses of LED on and off bytes
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09

# Addresses of ALL_LED on and off bytes
ALL_LED_ON_L = 0xfa
ALL_LED_ON_H = 0xfb
ALL_LED_OFF_L = 0xfc
ALL_LED_OFF_H = 0xfd


class PCA9685:
    """ Sets up and controls the PCA9685 I2C LED Controller. """

    def __init__(self, bus, address=ADDRESS):

        self.bus = smbus.SMBus(bus)
        self.address = address

    def enable(self):
        """ Enables the driver output. """
        self.bus.write_byte_data(self.address, MODE1, self.bus.read_byte_data(self.address, MODE1) & ~0x10)

    def disable(self):
        """ Disables the driver output. """
        self.bus.write_byte_data(self.address, MODE1, self.bus.read_byte_data(self.address, MODE1) | 0x10)

    def set_frequency(self, hertz):
        """ Set the PWM frequency for all outputs, within 24Hz - 1526Hz. """

        # Disable the Output
        self.disable()

        # Calculate the pre-scale value
        pre_scale = int(round((25 * pow(10, 6))/(4096 * hertz)) - 1)

        # Write the pre-scale value to the device
        self.bus.write_byte_data(self.address, PRE_SCALE, pre_scale)

        # Enable the Output
        self.enable()

    def set_pwm(self, duty_cycle, channel=None):
        """ Set the PWM of a specific channel, or all channels if channel is None. """

        # Calculate the pulse width
        width = round(4095 * duty_cycle)

        # Split into bytes
        off_l = width & 0xff
        off_h = (width >> 8) & 0x0f

        if channel is None:
            # Set the PWM for all channels
            self.bus.write_byte_data(self.address, ALL_LED_ON_L, 0x00)
            self.bus.write_byte_data(self.address, ALL_LED_ON_H, 0x00)

            self.bus.write_byte_data(self.address, ALL_LED_OFF_L, off_l)
            self.bus.write_byte_data(self.address, ALL_LED_OFF_H, off_h)

        elif 16 > channel >= 0:
            # Set the PWM for the channel
            offset = 4 * channel

            self.bus.write_byte_data(self.address, LED0_ON_L + offset, 0x00)
            self.bus.write_byte_data(self.address, LED0_ON_H + offset, 0x00)
            
            self.bus.write_byte_data(self.address, LED0_OFF_L + offset, off_l)
            self.bus.write_byte_data(self.address, LED0_OFF_H + offset, off_h)


class Dummy:

    def __init(self):
        pass

    def set_pwm(self, duty_cycle, channel=None):
        print("Setting PWM Duty Cycle: " + str(duty_cycle))
