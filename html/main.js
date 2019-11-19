let app = new Vue({
            el: '#app',
            data: {
                sensor: {
                    accel: [0, 0, 0],
                    gyro: [0, 0, 0],
                    mag: [0, 0, 0]
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
                },

                format_sensor_data: function(source) {
                    let sensor;
                    let digits;

                    if(source == "accel"){
                        sensor = this.sensor.accel;
                        digits = 2;
                    } else if(source == "gyro"){
                        sensor = this.sensor.gyro;
                        digits = 4;
                    } else if(source == "mag"){
                        sensor = this.sensor.mag;
                        digits = 4;
                    }

                    return `[ ${sensor[0].toFixed(digits)}, ${sensor[1].toFixed(digits)}, ${sensor[2].toFixed(digits)} ]`
                }
            }
        });