let app = new Vue({
            el: '#app',
            data: {
                logs: {
                    acceleration: [],
                    angularVelocity: [],
                    magneticField: []
                },
                motor: {
                    throttle: 0
                },
                test: {
                    type: "example"
                }
            },
            mounted: function() {

                // Create the Websocket
                const loc = window.location;
                const url = loc.protocol === "https:" ? "wss://" : "ws://";
                this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

                // Setup the callback to process received messages
                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);

                    if(message.type == "SENSOR_DATA"){
                        this.logs.acceleration.push(message.acceleration);
                        this.logs.angularVelocity.push(message.angularVelocity);
                        this.logs.magneticField.push(message.magneticField);
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

            }
        });