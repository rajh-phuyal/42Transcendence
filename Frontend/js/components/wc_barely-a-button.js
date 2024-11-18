class BarelyAButton extends HTMLElement
{
    constructor()
    {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes()
    {
        return["name", "route", "method", "datapayload", "onresolve", "buttonclass", "onerror"];
    }

    connectedCallback()
    {
        this.render();
        // this.shadow.addEventListener('click', this.method.bind(this));
    }

    attributeChangedCallback(name, oldValue, newValue)
    {
        if (name === "name")
            this.name = newValue;
        else if (name === "route")
            this.route = newValue;
        else if (name === "method")
            this.method = newValue;
        else if (name === "datapayload")
            this.datapayload = newValue;
        else if (name === "onresolve")
            this.onresolve = newValue;
        else if (name === "buttonclass")
            this.buttonclass = newValue;
        else if (name === "onerror")
            console.log("Error");
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
                    font-size: 20px;
                    vertical-align: middle;
                    text-align: center;
                    align-items: justify;
                    font-weight: 700;
                    color: #FFFCE6;
                    height: 30px;
                    width: 150px;
                    margin: 15px;
                    padding: 3px;
                    border: 2px solid  #595959;
                    border-radius: 8px;
                    background-color: #3D3D3D;
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