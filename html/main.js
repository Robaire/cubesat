let app = new Vue({
            el: '#app',
            data: {
                current: {
                    yaw: 0,
                    pitch: 0,
                    roll: 0
                },
                target: {
                    yaw: 0,
                    pitch: 0,
                    roll: 0
                }
            },
            mounted: function() {

                // Create the Websocket
                const loc = window.location;
                const url = loc.protocol === "https:" ? "wss://" : "ws://";
                this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

                // Setup the callback to process received messages
                this.ws.onmessage = (event) => {
                    this.current = JSON.parse(event.data);
                }
            },
            methods: {
                send_target: function() {
                    const message = JSON.stringify(this.target);
                    this.ws.send(message);
                }
            }
        });