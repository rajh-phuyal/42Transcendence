/* This is nice for syncing tabs. Since its not fully working and we don't want
to fail eval we just comment it out and will fix it in a second life ;) */

/* import events from "./events.js";

class Syncer {
    constructor() {
        this.id = crypto.randomUUID();
        // console.log("Syncer ID", this.id);

        this.broadcastChannel = new BroadcastChannel("barely-a-syncer");
        this._listen();
    }

    async _listen() {
        this.broadcastChannel.onmessage = async (event) => {
            // console.log("Syncer received message", event.data);
            const { type, payload, id } = event.data;
            if (id === this.id) return;

            await events[type](payload);
        };
    }

    broadcast(type, payload, includeSelf = true) {
        // console.log("Syncer broadcasting", type, payload, includeSelf ? this.id : null);
        this.broadcastChannel.postMessage({ type, payload, id: includeSelf ? this.id : null });
    }
}

const $syncer = new Syncer();
export default $syncer;
 */