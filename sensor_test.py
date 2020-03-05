import PCA9685
import BNO055
import LTC2945
import time

# Setup PCA9685
print("Initializing PWM Driver")
pwm = PCA9685.PCA9685(1)
pwm.set_frequency(50)

# Setup BNO055
print("Initializing IMU")
sensor = BNO055.BNO055(1)

# Setup LTC2945
print("Initializing Voltage Monitor")
power = LTC2945.LTC2945(1)

# Setup complete
print("Initialization complete")

counter = 0
while(True):

    vin = power.read_vin()
    current = power.read_current()

    print("Battery Voltage: " + str(vin))
    print("Current Consumption: " + str(vin))

    if counter == 5:
        pwm.set_duty_cycle(0.1, 0)
    elif counter > 10:
        pwm.set_duty_cycle(0.0, 0)
        counter = 0

    counter += 0.1
    time.sleep(0.5)
