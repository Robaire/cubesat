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


while(True):

    # print(power.read_vin())
    # print(power.read_sense())
    # print(power.read_current())
    # print(power.read_power())

    # print(sensor.read_accel())
    # print(sensor.read_gyro())

    # print(sensor.read_euler())
    # print(sensor.read_quaternion())
    # time.sleep(1)

    pwm.set_duty_cycle(0.1)
    time.sleep(10)
    pwm.set_duty_cycle(0.0)
    time.sleep(10)

