class BarelyAButton extends HTMLElement
{
    constructor()
    {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.height = 100;      // 100% of parent
        this.width = 100;       // 100% of parent
        this.fontsize = 1;      // 1vh
        this.name = undefined;
        this.route = undefined;
        this.height = undefined;
        this.method = undefined;
        this.datapayload = undefined;
        this.onresolve = undefined;
        this.color = "black";
    }

    static get observedAttributes()
    {
        return["name", "route", "method", "height", "width", "datapayload", "fontsize", "onresolve", "buttonclass", "onerror", "highlight"];
    }

    connectedCallback()
    {
        this.render();
        // this.shadow.addEventListener('click', this.method.bind(this));
    }

    attributeChangedCallback(name, oldValue, newValue)
    {
        if (["height", "width", "fontsize"].includes(name))
            this[name] = Number(newValue);
        else
            this[name] = newValue;


        if (name === "highlight") {
            if (newValue === "true")
                this.color = "#7B0101";
            else
                this.color = "black";
        }
        this.render();
    }

    render()
    {
        this.shadow.innerHTML = `
            <style>
               /*  .round-button{
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
                } */

                .rect-button{
                    font-family: 'Courier';
                    font-size: ${this.fontsize}vh;
                    vertical-align: middle;
                    text-align: center;
                    align-items: justify;
                    font-weight: 700;
                    color: #FFFCE6;
                    height: ${this.height}%;
                    width: ${this.width}%;
                    background-color: ${this.color};
                    cursor: pointer;
                    padding: 2px 4px;
                    border: 2px solid #968503;
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