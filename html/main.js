let app = new Vue({
            el: '#app',
            data: {
                logs: {
                    acceleration: [],
                    angularVelocity: [],
                    magneticField: []
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

                        console.log(this.logs)
                    }

                }
            },
            methods: {




                setDutycycle: function() {

                    const message = JSON.stringify(this.test);
                    this.ws.send(message);
                },

            }
        });