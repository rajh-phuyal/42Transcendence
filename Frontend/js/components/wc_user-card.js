class UserCard extends HTMLElement
{
    constructor()
    {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.cardOpened = false;
    }


    static get observedAttributes()
    {
        return["user", "onClickCallback", "image"];
    }
    
    connectedCallback()
    {
        this.render();
        this.shadow.addEventListener('click', this.onClickCallback.bind(this));
    }
    

    attributeChangedCallback(name, oldValue, newValue)
    {
        if (name === "user") {
            this.user = newValue;
            this.render();
        }
        else if (name === "onClickCallback") {
            this.onClickCallback = newValue;
            this.render();
        }
        else if (name === "image") {
            this.image = newValue;
            this.render();
        }
    }

    render()
    {
        this.shadow.innerHTML = `
            <style>
                .user-card-container{
                    display: flex;
                    font-family: 'Courier';
                    font-weight: 500;
                    width: 160px;
                    flex-direction: row;
                    margin: 15px;
                    padding: 3px;
                    border: 2px solid  #595959;
                    border-radius: 3px;
                    background-color: #FFF6D4;
                    cursor: pointer;
                }

                .user-card-container:hover{
                    background-color: #EFE6C4;
                }

                .user-div{
                    margin: 0;
                    padding: 12px 15px 0px 15px;
                }
                .image-div{
                    margin: 0;
                    width: 50px;
                    height: 50px;
                    border-radius: 8px;
                }
            </style>
            <div class="user-card-container">
            <img class = "image-div" src="${this.image}">
            <p class="user-div" > ${this.user} </p>
            </div>
        `;
    }

    
}


customElements.define("user-card", UserCard);





// https://www.youtube.com/watch?v=vLkPBj9ZaU0
// https://www.youtube.com/watch?v=2I7uX8m0Ta0