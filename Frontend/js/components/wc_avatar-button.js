class AvatarButton extends HTMLElement
{
    constructor()
    {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes()
    {
        return["image", "user", "redir"];
    }

    connectedCallback()
    {
        this.render();
    }

    attributeChangedCallback(name, oldValue, newValue)
    {
        if (name === "user")
            this.user = newValue;
        else if (name === "image")
            this.image = newValue;
        else if (name === "redir")
        {
            if (newValue === "true")
                this.is_redir = true;
            else
                this.is_redir = false;
        }
        this.render();
    }

    render()
    {
        console.log(this.image);
        this.shadow.innerHTML = `
            <style>
                img{
                    margin: 0;
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    cursor: pointer;
                }

                img:hover{
                    width: 52px;
                    height: 52px;
                    outline: 2px;
                }

                img:active{
                    width: 50px;
                    height: 50px;
                }
            </style>
            <img class="image-div" src="${this.image}">
            </img>
        `;
    }

}

customElements.define("avatar-button", AvatarButton);