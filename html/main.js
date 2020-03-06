let app = new Vue({
    el: '#app',
    data: {
        voltage: 0,
        current: 0,
        target: {x: 0, y: 0, z: 0},
        euler: {x: 0, y: 0, z: 0},
        wheel: {x: 0, y: 0, z: 0}
    },

    mounted: function() {

        // Create the Websocket
        const loc = window.location;
        const url = loc.protocol === "https:" ? "wss://" : "ws://";
        this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

        // Setup the callback to process received messages
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            if(message.type == "POWER_DATA"){
                this.voltage = message.voltage;
                this.current = message.current;
            }

            if(message.type == "EULER_DATA"){
                this.euler.x = message.x;
                this.euler.y = message.y;
                this.euler.z = message.z;
            }

            if(message.type == "WHEEL_DATA"){
                this.wheel.x = message.x;
                this.wheel.y = message.y;
                this.wheel.z = message.z;
            }

            if(message.type == "TARGET_DATA"){
                this.target.x = message.x;
                this.target.y = message.y;
                this.target.z = message.z;
            }

        }
    },

    methods: {
        sendMessage: function(header, body) {
            const message = JSON.stringify({header: header, body: body});
            this.ws.send(message);
        },
        setThrottle: function() {
            // Sends the motor throttle
            this.sendMessage("MOTOR_SPEED", this.motor);
        }

    },

    filters: {
        short: function(number) {
            return number.toFixed(2)
        },
        long: function(number) {
            return number.toFixed(6)
        }
    }
});