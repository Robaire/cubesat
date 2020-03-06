from yaml import load, Loader
import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import PCA9685
import BNO055
import LTC2945

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
    euler = BNO055.BNO055(1)

    # Setup LTC2945
    print("Initializing Voltage Monitor")
    power = LTC2945.LTC2945(1)

    # Setup complete
    print("Initialization complete")

else:
    # Create fake devices for testing
    pwm = PCA9685.Dummy()
    euler = BNO055.Dummy()
    power = LTC2945.Dummy()

# Set the port for the web server
port = config.get('port', 8080)

# Global State
state = {
    'isEnabled': False,
    'controlOptions': ['None', 'Proportional', 'Bang-Bang', 'PID'],
    'activeControl': 'None',
    'controlSettings': {
        'proportional': {'constant': 0.001},
        'bangbang': {
            'threshold': 5,
            'strength': 10,
        },
        'pid': {'p': 0, 'i': 0, 'd': 0},
        'target': {'x': 0, 'y': 0, 'z': 0}
    }
}

# Most Recent Sensor Data
sensor = {
    'voltage': 0,
    'current': 0,
    'euler': {'x': 0, 'y': 0, 'z': 0},
    'wheel': {'x': 0, 'y': 0, 'z': 0}
}


def set_state(body):
    """ Sends most recent state data to all clients. """

    # Update the global state
    global state
    state = body
    message = json.dumps({
        'type': 'STATE',
        'body': state
    })

    # Alert all clients of the new global state
    for client in SocketHandler.clients:
        client.write_message(message)


def set_sensor():
    """ Sends most recent sensor data to all clients. """

    message = json.dumps({
        'type': 'SENSOR',
        'body': sensor
    })

    for client in SocketHandler.clients:
        client.write_message(message)


def poll_sensors():
    """ Updates stored sensor values. """

    global sensor
    sensor['voltage'] = power.read_vin()
    sensor['current'] = power.read_current()
    angles = euler.read_euler()
    sensor['euler'] = {'x': angles[1], 'y': -angles[2], 'z': -angles[0]}


def controller():
    """ Handles all control logic. """

    if state['isEnabled']:

        # Get the current and target positions
        target = state['controlSettings']['target']
        position = sensor['euler']

        # Compare the positions
        dx = target['x'] - position['x']
        dy = target['y'] - position['y']
        dz = target['z'] - position['z']

        # Determine which control mode to use
        if state['activeControl'] == 'None':
            pwm.set_throttle(0)
            sensor['wheel'] = {'x': 0, 'y': 0, 'z': 0}

        if state['activeControl'] == 'Proportional':

            # Retrieve settings from the state
            constant = float(state['controlSettings']['proportional']['constant'])

            # Saturate the function values at 1 or -1
            dx = max(min(dx * constant, 1), -1)
            dy = max(min(dy * constant, 1), -1)
            dz = max(min(dz * constant, 1), -1)

            pwm.set_throttle(dx, 0)
            pwm.set_throttle(dy, 2)
            pwm.set_throttle(dz, 1)

            sensor['wheel'] = {'x': dx, 'y': dy, 'z': dz}

        if state['activeControl'] == 'Bang-Bang':

            # Retrieve settings from the state
            settings = state['controlSettings']['bangbang']
            threshold = float(settings['threshold'])
            strength = float(settings['strength']) / 100

            # Set the throttle based on the sign of the results
            if abs(dx) < threshold:
                pwm.set_throttle(0, 0)
                sensor['wheel']['x'] = 0
            elif dx > 0:
                pwm.set_throttle(1 * strength, 0)
                sensor['wheel']['x'] = 1 * strength
            elif dx < 0:
                pwm.set_throttle(-1 * strength, 0)
                sensor['wheel']['x'] = -1 * strength

            if abs(dy) < threshold:
                pwm.set_throttle(0, 2)
                sensor['wheel']['y'] = 0
            elif dy > 0:
                pwm.set_throttle(1 * strength, 2)
                sensor['wheel']['y'] = 1 * strength
            elif dy < 0:
                pwm.set_throttle(-1 * strength, 2)
                sensor['wheel']['y'] = -1 * strength

            if abs(dz) < threshold:
                pwm.set_throttle(0, 1)
                sensor['wheel']['z'] = 0
            elif dz > 0:
                pwm.set_throttle(1 * strength, 1)
                sensor['wheel']['z'] = 1 * strength
            elif dz < 0:
                pwm.set_throttle(-1 * strength, 1)
                sensor['wheel']['z'] = -1 * strength

        if state['activeControl'] == 'PID':
            pwm.set_throttle(0)
            sensor['wheel'] = {'x': 0, 'y': 0, 'z': 0}

    else:
        # Disable all motors
        pwm.set_throttle(0)
        sensor['wheel'] = {'x': 0, 'y': 0, 'z': 0}


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
            # "ENABLE": set_enable_state,
            # "CONTROL": set_control_state,
            # "CONTROL_SETTINGS": set_control_settings,
            "STATE": set_state
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
    tornado.ioloop.PeriodicCallback(poll_sensors, 10).start()
    tornado.ioloop.PeriodicCallback(controller, 10).start()
    tornado.ioloop.PeriodicCallback(set_sensor, 500).start()
    tornado.ioloop.IOLoop.current().start()
