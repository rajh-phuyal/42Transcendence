class BarelyAButton extends HTMLElement
{
    constructor()
    {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.height = 4;
        this.width = 8;
        this.fontSize = 2;
        this.name = undefined;
        this.route = undefined;
        this.height = undefined;
        this.height = undefined;
        this.fontSize = undefined;
        this.method = undefined;
        this.datapayload = undefined;
        this.onresolve = undefined;
    }

    static get observedAttributes()
    {
        return["name", "route", "method", "height", "width", "datapayload", "fontsize", "onresolve", "buttonclass", "onerror"];
    }

    connectedCallback()
    {
        this.render();
        // this.shadow.addEventListener('click', this.method.bind(this));
    }

    attributeChangedCallback(name, oldValue, newValue)
    {
        this[name] = newValue;
        this.render();
    }

    render()
    {
        this.shadow.innerHTML = `
            <style>
                .round-button{
                    display: flex;
                    font-family: 'Courier';
                    align-items: justify;
                    text-align: justify;
                    line-height: 50px;
                    font-weight: 700;
                    color: #FFFCE6;
                    width: 60px;
                    flex-direction: row;
                    margin: 15px;
                    padding: 3px;
                    border: 2px solid  #595959;
                    border-radius: 100%;
                    background-color: #3D3D3D;
                    cursor: pointer;
                }

                .rect-button{
                    font-family: 'Courier';
                    font-size: ${this.fontSize}vh;
                    vertical-align: middle;
                    text-align: center;
                    align-items: justify;
                    font-weight: 700;
                    color: #FFFCE6;
                    height: ${this.height}vh;
                    width: ${this.width}vw;
                    background-color: #000000;
                    cursor: pointer;
                }

                button:hover {
                    background-color: #4a4a4a;
                }
                button:active{
                    background-color: #333333;
                }
            </style>
            <button class=${this.buttonclass} > ${this.name} </button>
        `;
    }

}

customElements.define("barely-a-button", BarelyAButton);


// <barely-a-button route="/battle"  method="post" data-payload="localViewDate" onresolve="someMethodDefinedOnView"></barely-a-button>