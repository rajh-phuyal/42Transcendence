class SearchBar extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes() {
        return ["placeholder", "width"];
    }

    connectedCallback() {
        this.render();
        const inputElement = this.shadow.getElementById("searchBarButton");
        inputElement.addEventListener('click', this.handleClick.bind(this));
        const inputElement2 = this.shadow.getElementById("input-bar");
        inputElement2.addEventListener('keypress', this.handleKeyPress.bind(this));
    }

    handleClick() {
        
        const inputElement = this.shadow.getElementById("input-bar");
        const value = inputElement.value;
        console.log("input value:", value);
    }

    handleKeyPress(event){

        if (event.key === 'Enter'){
            const inputElement = event.target;
            const value = inputElement.value;
            console.log("input value:", value);
        }

    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "placeholder") {
            this.placeholder = newValue;
        } else if (name === "width") {
            this.width = newValue;
        }
        this.render();
    }

    render() {
        this.shadow.innerHTML = `
            <style>
                .container {
                    display: flex;
                    align-items: center;
                    font-size: 25px;
                    text-align: center;
                    line-height: 50px;
                    font-weight: 700;
                    color: #FFFCE6;
                    width: ${this.width || '150'}px;
                    flex-direction: row;
                    margin: 15px;
                    padding: 3px;
                    border: 2px solid  #595959;
                    border-radius: 8px;
                    background-color: #3D3D3D;
                }


                input {
                    font-size: 16px;
                    font-family: 'Courier';
                    color: #FFFCE6;
                    font-weight: 600;
                    flex: 1;
                    padding: 5px;
                    border: none;
                    border-radius: 8px;
                    outline: none;
                    background-color: #3D3D3D;
                }

                input:hover{
                    background-color: #4a4a4a;
                }
                
                input:focus{
                    background-color: #4a4a4a;
                }

                button {
                    font-family: 'Courier';
                    font-size: 16px;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    background-color: #595959;
                    color: #FFFCE6;
                    margin-left: 5px;
                }

                button:hover {
                    background-color: #4a4a4a;
                }
                
                button:active{
                    background-color: #333333;
                }
            </style>

            <div class="container">
                <input id="input-bar" type="search" placeholder="${this.placeholder || 'Search...'}" class="search-box">
                <button id="searchBarButton">Go</button>
            </div>
        `;
    }
}

customElements.define("search-bar", SearchBar);


