import tornado.ioloop
import tornado.web
import tornado.websocket
from asyncio import sleep
import json
import PCA9685

# Setup i2c
pwm = PCA9685.PCA9685(1, 0x40)
pwm.set_frequency(50)

# List of connected clients
clients = set()

state = {
    'yaw': 0,
    'pitch': 0,
    'roll': 0
}


async def broadcast():
    """ Callback to push info to the clients"""
    while True:
        for client in clients:
            await client.write_message(json.dumps(state))

        await sleep(0.1)


class SocketHandler(tornado.websocket.WebSocketHandler):
    """ Handles all socket requests from the client. """

    def open(self):
        # Add the client to the client list
        clients.add(self)

    def on_message(self, message):
        global state
        # state = json.loads(message)
        duty_cycle = json.loads(message)
        pwm.set_pwm(duty_cycle)

    def on_close(self):
        # Remove the socket connection
        clients.remove(self)


# Main Entry
if __name__ == "__main__":

    # Create the application and route table
    app = tornado.web.Application([
        (r"/ws", SocketHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {'path': './html', 'default_filename': 'index.html'})
    ])

    # Start the server
    app.listen(8181)
    tornado.ioloop.IOLoop.current().add_callback(broadcast)
    tornado.ioloop.IOLoop.current().start()
