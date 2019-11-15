let app = new Vue({
            el: '#app',
            data: {
                sensor_data: {
                    accelerometer: {
                        x: [],
                        y: [],
                        z: [],
                        t: []
                    },
                    gyroscope: {
                        x: [],
                        y: [],
                        z: [],
                        t: []
                    },
                    magnetometer: {
                        x: [],
                        y: [],
                        z: [],
                        t: []
                    }
                },
                state: {
                    position: {
                        yaw: [],
                        pitch: [],
                        roll: [],
                        t: []
                    },
                    velocity: {
                        yaw: [],
                        pitch: [],
                        roll: [],
                        t: []
                    }
                },
                commands: {
                    position: {
                        yaw: 0,
                        pitch: 0,
                        roll: 0
                    }
                }
            },
            mounted: function() {

                // Create the Websocket
                const loc = window.location;
                const url = loc.protocol === "https:" ? "wss://" : "ws://";
                this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

                // Setup the callback to process received messages
                this.ws.onmessage = (event) => {
                    // this.current = JSON.parse(event.data);
                }
            },
            methods: {
                send_commands: function() {
                    const message = JSON.stringify(this.commands);
                    this.ws.send(message);
                }
            }
        });