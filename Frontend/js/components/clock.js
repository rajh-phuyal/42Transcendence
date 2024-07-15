class ClockDisplay extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.intervalId = null;
    }

    connectedCallback() {
        this.render();
        this.startClock();
    }

    disconnectedCallback() {
        this.stopClock();
    }

    startClock() {
        this.intervalId = setInterval(() => this.render(), 1000);
    }

    stopClock() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    render() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    font-family: Arial, sans-serif;
                    background: #f0f0f0;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    font-size: 1.2em;
                }
            </style>
            <div>
                <p>Current Time: ${timeString}</p>
            </div>
        `;
    }
}

customElements.define('clock-display', ClockDisplay);
