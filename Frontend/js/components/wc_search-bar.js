import call from "../abstracts/call.js";

class SearchBar extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.searchResults = [];
        this.searchType = "users";
        this.onlySearchFriends = false;
        this.includeSelf = false;
        this.width = "300";
        this.onClickEvent = "select-user";
        this.clearOnClick = false;
        this.debounceTimeout = null;
        this.lastInputValue = "";
    }

    static get observedAttributes() {
        return ["width", "search-type", "on-click-event", "clear-on-click", "only-search-friends", "include-self"];
    }

    reRenderAndAttach() {
        this.render();
        this.shadow.getElementById("input-bar").addEventListener('input', this.handleKeyInput.bind(this));
        this.shadow.getElementById("input-bar").addEventListener('keydown', this.handleKeydown.bind(this));
        this.shadow.getElementById("input-bar").addEventListener('blur', this.handleBlur.bind(this));
    }

    connectedCallback() {
        this.reRenderAndAttach();
    }

    handleKeyInput(event) {
        const value = event.target.value.trim();
        this.lastInputValue = value; // To avoid race conditions

        if (!value) {
            this.searchResults = [];
            this.updateSearchResults(this.searchType, value);
            return;
        }

        clearTimeout(this.debounceTimeout);

        this.debounceTimeout = setTimeout(() => {
            const endpoint = {
                "users": `user/search/${value}/`,
                "tournaments": `tournament/to-join/`
            }

            let filter = ""
            if (this.onlySearchFriends)
                filter = "?onlyFriends=true"
            if (this.includeSelf)
                filter += filter ? "&includeSelf=true" : "?includeSelf=true";
            call(endpoint[this.searchType] + filter, 'GET')
                .then(response => {
                    if (this.lastInputValue !== value) return;
                    this.searchResults = response?.[this.searchType] || [];
                    this.updateSearchResults(this.searchType, value);
                })
                .catch(error => {
                    console.error("Error fetching search results:", error);
                    this.searchResults = [];
                    this.updateSearchResults(this.searchType, value);
                });
        }, 300); // delay to allow the input to be typed
    }

    handleKeydown(event) {
        if (event.key === "Escape") {
            // Esc clears the input
            this.shadow.getElementById("input-bar").value = "";
            this.handleKeyInput(event);
        } else if (event.key === "Enter") {
            // Enter -> selects first result exists, then trigger click
            if (this.searchResults.length > 0) {
                const firstItem = this.shadow.querySelector('.dropdown div');
                if (firstItem)
                    firstItem.click();
            }
        }
    }

    handleBlur(event) {
        setTimeout(() => {
            this.shadow.getElementById("input-bar").value = "";
            this.searchResults = [];
            const dropdown = this.shadow.querySelector('.dropdown');
            dropdown.innerHTML = "";
            dropdown.style.display = 'none';
        }, 500); // Delay just enough to let click event fire so the client can click on the dropdown
    }

    updateSearchResults(type, value) {
        const dropdown = this.shadow.querySelector('.dropdown');
        if (!dropdown) return;

        if (!this.searchResults.length && !value) {
            /* Input is empty */
            this.searchResults = [];
            dropdown.innerHTML = "";
            dropdown.style.display = 'none';
            return;
        } else if (!this.searchResults.length) {
            /* No results */
            this.searchResults = [];
            dropdown.innerHTML = "";
            dropdown.style.display = 'block'
            const emptyMessage = document.createElement('div');
            emptyMessage.classList.add('no-results');
            emptyMessage.textContent = "❌ 🔍 ❌"
            emptyMessage.style.textAlign = "center";
            dropdown.appendChild(emptyMessage);
            return;
        }

        const innerHTML = type === "tournaments" ? this.searchResults
            .filter(tournament => tournament.tournamentName.includes(value))
            .map(tournament => `
                <div id="tournament-item-${tournament.id}" class="tournament-item">
                    <span class="tournament-name">${tournament.tournamentName}</span>
                </div>
            `).join('') : this.searchResults
            .map(user => `
                <div id="user-item-${user.id}" class="user-item">
                    <img src="${window.origin}/media/avatars/${user.avatar}"
                         alt="${user.username}"
                         class="user-image"
                         draggable="false">
                    <span class="user-name">${user.username}</span>
                </div>
            `).join('');

        dropdown.innerHTML = innerHTML;
        dropdown.style.display = 'block';

        // Add event listeners to each item
        for (const item of this.searchResults) {
            const idPrefix = this.searchType === "users" ? "user" : "tournament";
            const element = this.shadow.getElementById(`${idPrefix}-item-${item.id}`);

            element.addEventListener('click', () => {
                window.dispatchEvent(new CustomEvent(this.onClickEvent, { detail: { [idPrefix]: item } }));
                if (this.clearOnClick) {
                    this.shadow.getElementById("input-bar").value = "";
                    this.searchResults = [];
                    dropdown.innerHTML = "";
                    dropdown.style.display = 'none';
                }
            });
        }
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "width") {
            this.width = newValue;
        } else if (name === "search-type") {
            this.searchType = newValue;
        } else if (name === "on-click-event") {
            this.onClickEvent = newValue;
        } else if (name === "clear-on-click") {
            this.clearOnClick = newValue;
        } else if (name === "only-search-friends") {
            this.onlySearchFriends = newValue === "true";
        } else if (name === "include-self") {
            this.includeSelf = newValue === "true";
        }
        this.render();
    }

    render() {
        this.shadow.innerHTML = `
            <style>
                .container {
                    position: relative;
                    display: flex;
                    align-items: center;
                    width: ${this.width || '300'}px;
                    margin: 5px;
                    background-color: #F5E6BE;
                    border: 2px solid #2A2A2A;
                    box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2);
                }

                input {
                    width: 100%;
                    font-family: 'Times New Roman', serif;
                    font-size: min(1vw, 15px);
                    padding: 10px;
                    border: none;
                    background-color: #000000;
                    color: #ffffff;
                    outline: none;
                }

                .dropdown {
                    position: absolute;
                    top: calc(100% - 1px);
                    left: 0px;
                    width: 100%;
                    margin: 0px !important;
                    margin-left: -1.5px !important;
                    background-color: #F5E6BE;
                    border: 2px solid #2A2A2A;
                    border-top: none;
                    box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2);
                    z-index: 1000;
                    padding: 2px 0;
                }

                .dropdown-content {
                    display: none;
                }

                input:focus + .dropdown {
                    display: block;
                }

                .tournament-item {
                    display: flex;
                    align-items: center;
                    padding: 8px 12px;
                    border-bottom: 1px solid rgba(42, 42, 42, 0.2);
                    cursor: pointer;
                    background-color: #F5E6BE;
                    color: #2A2A2A;
                    gap: 12px;
                }

                .user-item {
                    display: flex;
                    align-items: center;
                    padding: 8px 12px;
                    border-bottom: 1px solid rgba(42, 42, 42, 0.2);
                    cursor: pointer;
                    background-color: #F5E6BE;
                    color: #2A2A2A;
                    gap: 12px;
                }

                .user-item:last-child {
                    border-bottom: none;
                }

                .user-image {
                    width: 21px;
                    height: 28px;
                    border: 1px solid #2A2A2A;
                    flex-shrink: 0;
                }

                .user-name {
                    font-family: 'Times New Roman', serif;
                    font-size: 16px;
                    font-weight: normal;
                    line-height: 1.2;
                }

                input::placeholder {
                    color: #666;
                    font-style: italic;
                }
            </style>

            <div class="container">
                <!-- THE PLACEHOLDER ARE JUST DOTS SO WE DON'T HAVE TO TRANSLATE THEM - TRANSLATION WILL BE IN TITLE / TOOLTIP -->
                <input id="input-bar" type="text" placeholder="..." class="search-box">
                <div class="dropdown" style="display: none"></div>
            </div>
        `;
    }
}

customElements.define("search-bar", SearchBar);


