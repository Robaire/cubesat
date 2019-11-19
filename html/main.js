let app = new Vue({
            el: '#app',
            data: {
                sensor: {
                    accel: [],
                    gyro: [],
                    mag: []
                },
                pwm: 50
            },
            mounted: function() {

                // Create the Websocket
                const loc = window.location;
                const url = loc.protocol === "https:" ? "wss://" : "ws://";
                this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

                // Setup the callback to process received messages
                this.ws.onmessage = (event) => {
                    this.sensor = JSON.parse(event.data);
                }
            },
            methods: {
                set_dutycycle: function() {
                    const message = JSON.stringify(this.pwm);
                    this.ws.send(message);
                }
            }
        });