let app = new Vue({
    el: '#app',
    data: {

        // Server State
        state: {
            // Enable Button
            isEnabled: false,

            // Control Selections
            controlOptions: ["None", "Proportional", "Bang-Bang", "PID"],
            activeControl: "None",

            // Active Control Settings
            controlSettings: {
                proportional: {
                    constant: 0
                },
                bangbang: {
                    threshold: 0,
                    strength: 0
                },
                pid: {p: 0, i: 0, d: 0},
                target: {x: 0, y: 0, z: 0}
            }
        },

        // Recent Sensor Data
        sensor: {
            voltage: 0,
            current: 0,
            euler: {x: 0, y: 0, z: 0},
            wheel: {x: 0, y: 0, z: 0}
        },

        // Client Management
        newTarget: {x: 0, y: 0, z: 0},
    },

    mounted: function() {

        // Create the Websocket
        const loc = window.location;
        const url = loc.protocol === "https:" ? "wss://" : "ws://";
        this.ws = new WebSocket(url + loc.host + loc.pathname + "ws");

        // Setup the callback to process received messages
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            switch(message.type.toString()){
                case "SENSOR":
                    this.sensor = message.body;
                    break;
                case "STATE":
                    this.state = message.body;
                    break;
                default:
                    console.log("Unknown message received!");
                    break;
            }
        }
    },

    methods: {
        updateState: function(){
            const message = JSON.stringify({header: "STATE", body: this.state});
            this.ws.send(message);
        },
        toggleEnable: function() {
            this.state.isEnabled = !this.state.isEnabled;
            this.updateState();
        },
        updateTarget: function(){
            this.state.controlSettings.target = this.newTarget;
            this.newTarget = {x: 0, y: 0, z: 0};
            this.updateState();
        }
    },

    filters: {
        short: function(number) {
            if(number) {
                return number.toFixed(2)
            } else {
                return 0
            }
        },
        long: function(number) {
            if(number) {
                return number.toFixed(3)
            } else {
                return 0
            }        }
    }
});