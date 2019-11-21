from yaml import load, Loader
import tornado.ioloop
import tornado.web
import tornado.websocket
from asyncio import sleep
import json
import PCA9685
import BNO055

# Read in run config
with open("config.yml", 'r') as file:
    config = load(file, Loader=Loader)

# Load necessary interfaces
if config['mode'] == 'full':

    # Setup PCA9685
    print("Setting up PWM Driver")
    pwm = PCA9685.PCA9685(1)
    pwm.set_frequency(50)
    pwm.set_pwm(0)

    # Setup BNO055
    print("Setting up Sensor")
    sensor = BNO055.BNO055(1)

else:

    # Create fake devices for testing
    pwm = PCA9685.Dummy()
    sensor = BNO055.Dummy()

# Set the port for the web server
port = config.get('port', 8080)


# async def broadcast():
#     """ Callback to push info to the clients"""
#     while True:
#         for client in clients:
#
#             await client.write_message(json.dumps(state))
#
#         await sleep(0.1)


# def send_sensor_data():
#
#     data = {
#         'accel': sensor.read_accel(),
#         'gyro': sensor.read_gyro(),
#         'mag': sensor.read_mag()
#     }
#
#     for client in clients:
#         client.write_message(json.dumps(data))

def send_sensor_data():

    data = {
        'type': 'SENSOR_DATA',
        'acceleration': sensor.read_accel(),
        'angularVelocity': sensor.read_gyro(),
        'magneticField': sensor.read_mag()
    }

    for client in SocketHandler.clients:
        client.write_message(json.dumps(data))


class SocketHandler(tornado.websocket.WebSocketHandler):
    """ Handles all socket requests from the client. """

    # Set of clients connected to this socket
    clients = set()

    def open(self):
        # Add the client to the client list
        self.clients.add(self)

    def on_close(self):
        # Remove the socket connection
        self.clients.remove(self)

    def on_message(self, message):

        # Read the message in as JSON
        data = json.loads(message)

        # Validate the message format
        try:
            header = data["type"]
        except:
            print("Improperly formatted message!")
            print(message)
            return

        # Map of handler functions for different messages
        handlers = {
            "example": None
        }

        # Call the appropriate handler
        if header in handlers:

            # Call the handler function
            try:
                handlers[header]()
            except:
                return
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
    pc = tornado.ioloop.PeriodicCallback(send_sensor_data, 200)
    pc.start()
    tornado.ioloop.IOLoop.current().start()
