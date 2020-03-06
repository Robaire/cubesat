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
                pid: {
                    p: 0,
                    i: 0,
                    d: 0
                },
                target: {x: 0, y: 0, z: 0}
            }
        },

        newTarget: {x: 0, y: 0, z: 0},

        // Sensor Display Values
        voltage: 0,
        current: 0,
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

            switch(message.type.toString()){
                case "POWER_DATA":
                    this.voltage = message.voltage;
                    this.current = message.current;
                    break;
                case "EULER_DATA":
                    this.euler.x = message.x;
                    this.euler.y = message.y;
                    this.euler.z = message.z;
                    break;
                case "WHEEL_DATA":
                    this.wheel.x = message.x;
                    this.wheel.y = message.y;
                    this.wheel.z = message.z;
                    break;
                case "STATE":
                    this.state = message.body;
                    break;

            }


        }
    },

    methods: {
        sendMessage: function(header, body) {
            // Sends a message to the server
            const message = JSON.stringify({header: header, body: body});
            this.ws.send(message);
        },
        toggleEnable: function() {
            this.state.isEnabled = !this.state.isEnabled;
            this.sendMessage("ENABLE", this.state.isEnabled);
        },

        updateControl: function(){
            this.sendMessage("CONTROL", this.state.activeControl);
        },

        updateControlSettings: function(){
            this.sendMessage("CONTROL_SETTINGS", this.state.controlSettings);
        },

        updateTarget: function(){
            this.state.controlSettings.target = this.newTarget;
            this.newTarget = {x: 0, y: 0, z: 0};
            this.updateControlSettings();
        }
    },

    filters: {
        short: function(number) {
            return number.toFixed(2)
        },
        long: function(number) {
            return number.toFixed(2)
        }
    }
});