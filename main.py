from yaml import load, Loader
import tornado.ioloop
import tornado.web
import tornado.websocket
from asyncio import sleep
import json
import PCA9685
import BNO055
import LTC2945

import random

# Read in run config
with open("config.yml", 'r') as file:
    config = load(file, Loader=Loader)

# Load necessary interfaces
if config['mode'] == 'full':

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

else:

    # Create fake devices for testing
    pwm = PCA9685.Dummy()
    sensor = BNO055.Dummy()
    power = LTC2945.Dummy()


# Set the port for the web server
port = config.get('port', 8080)

# Outgoing Data Handlers
def send_euler_data():

    euler = sensor.read_euler()

    message = json.dumps({
        'type': 'EULER_DATA',
        'x': euler[0],
        'y': euler[1],
        'z': euler[2]
    })

    for client in SocketHandler.clients:
        client.write_message(message)


def send_wheel_data():

    message = json.dumps({
        'type': 'WHEEL_DATA',
        'x': random.random(),
        'y': random.random(),
        'z': random.random()
    })

    for client in SocketHandler.clients:
        client.write_message(message)


def send_power_data():

    message = json.dumps({
        'type': 'POWER_DATA',
        'voltage': power.read_vin(),
        'current': power.read_current()
    })

    for client in SocketHandler.clients:
        client.write_message(message)


def send_target_data():

    message = json.dumps({
        'type': 'TARGET_DATA',
        'x': random.random(),
        'y': random.random(),
        'z': random.random()
    })

    for client in SocketHandler.clients:
        client.write_message(message)


def send_data():
    send_euler_data()
    send_wheel_data()
    send_power_data()
    send_target_data()

# Incoming Data Handlers
def setMotorSpeed(body):
    throttle = body["throttle"]

    # Map the throttle value onto the correct range
    duty_cycle = 0.05 + ((throttle / 100) * 0.05)

    print(f'Throttle: {throttle}%, Duty Cycle: {duty_cycle}, Pulse Width: {duty_cycle * 20}ms')

    # Set the PWM driver to output the new duty cycle
    pwm.set_duty_cycle(duty_cycle)


# Global State
state = {
    'isEnabled': False,
    'controlOptions': ['None', 'Proportional', 'Bang-Bang', 'PID'],
    'activeControl': 'None',
    'controlSettings': {
        'proportional': {'constant': 0},
        'bangbang': {
            'threshold': 0,
            'strength': 0,
        },
        'pid': {
            'p': 0,
            'i': 0,
            'd': 0
        },
        'target': {
            'x': 100,
            'y': -20,
            'z': 18
        }
    }
}


def send_state():
    """ Sends the entire state to all connected clients. """
    message = json.dumps({
        'type': 'STATE',
        'body': state
    })
    for client in SocketHandler.clients:
        client.write_message(message)


def set_enable_state(body):
    state['isEnabled'] = body
    send_state()


def set_control_state(body):
    state['activeControl'] = body
    send_state()

def set_control_settings(body):
    state['controlSettings'] = body
    send_state()

class SocketHandler(tornado.websocket.WebSocketHandler):
    """ Handles all socket requests from the client. """

    # Set of clients connected to this socket
    clients = set()

    def open(self):
        # Add the client to the client list
        self.clients.add(self)

        # Send the client the most recent state available
        message = json.dumps({
            'type': 'STATE',
            'body': state
        })
        self.write_message(message)

    def on_close(self):
        # Remove the socket connection
        self.clients.remove(self)

    def on_message(self, message):

        # Read the message in as JSON
        data = json.loads(message)

        # Validate the message format
        try:
            header = data["header"]
        except:
            print("Improperly formatted message!")
            print(message)
            return

        # Map of handler functions for different messages
        handlers = {
            "example": None,
            "MOTOR_SPEED": setMotorSpeed,
            "ENABLE": set_enable_state,
            "CONTROL": set_control_state,
            "CONTROL_SETTINGS": set_control_settings
        }

        # Call the appropriate handler
        if header in handlers:

            # Call the handler function
            try:
                handlers[header](data["body"])
            except:
                print("Error calling handler function for: " + header)
        else:
            print("Unrecognized message type!")
            print(data)


# Main Entry
if __name__ == "__main__":

    # Create the application and route table
    app = tornado.web.Application([
        (r"/ws", SocketHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {'path': './html', 'default_filename': 'index.html'})
    ])

    # Start the server
    app.listen(port)
    pc = tornado.ioloop.PeriodicCallback(send_data, 800)
    pc.start()
    tornado.ioloop.IOLoop.current().start()
