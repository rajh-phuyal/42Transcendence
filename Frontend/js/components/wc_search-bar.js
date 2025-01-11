import call from "../abstracts/call.js";

class SearchBar extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.searchResults = [];
        this.searchType = "users";
        this.width = "300";
    }

    static get observedAttributes() {
        return ["placeholder", "width", "search-type"];
    }

    reRenderAndAttach() {
        this.render();
        this.shadow.getElementById("input-bar").addEventListener('input', this.handleKeyPress.bind(this));
    }

    connectedCallback() {
        this.reRenderAndAttach();
    }

    handleKeyPress(event) {
        const value = event.target.value.trim();

        // Clear results if input is empty
        if (!value) {
            this.searchResults = [];
            this.updateSearchResults(this.searchType, value);
            return;
        }

        const endpoint = {
            "users": `user/search/${value}/`,
            "tournaments": `tournament/to-join/`
        }
        console.log(endpoint[this.searchType]);

        call(endpoint[this.searchType], 'GET')
            .then(response => {
                this.searchResults = response?.[this.searchType] || [];
                this.updateSearchResults(this.searchType, value);
            })
            .catch(error => {
                console.error("Error fetching search results:", error);
                this.searchResults = []; // Clear results on error
                this.updateSearchResults(this.searchType, value);
            });
    }

    // Add new method to update only the search results
    updateSearchResults(type, value) {
        const dropdown = this.shadow.querySelector('.dropdown');
        if (!dropdown) return;

        // If no results, just hide the dropdown
        if (!this.searchResults.length) {
            dropdown.style.display = 'none';
            return;
        }

        const innerHTML = type === "tournaments" ? this.searchResults
            .filter(tournament => tournament.tournamentName.includes(value))
            .map(tournament => `
                <div class="tournament-item">
                    <span class="tournament-name">${tournament.tournamentName}</span>
                </div>
            `).join('') : this.searchResults
            .map(player => `
                <div class="user-item">
                    <img src="${window.origin}/media/avatars/${player.avatar_path}"
                         alt="${player.username}"
                         class="player-image">
                    <span class="player-name">${player.username}</span>
                </div>
            `).join('');

        dropdown.innerHTML = innerHTML;
        dropdown.style.display = 'block';
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "placeholder") {
            this.placeholder = newValue;
        } else if (name === "width") {
            this.width = newValue;
        } else if (name === "search-type") {
            this.searchType = newValue;
        }
        this.render();
    }

    render() {
        console.log(this.searchType);
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
                    font-size: 20px;
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

                .player-image {
                    width: 32px;
                    height: 32px;
                    border: 1px solid #2A2A2A;
                    flex-shrink: 0;
                }

                .player-name {
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
                <input id="input-bar" type="text" placeholder="${this.placeholder || 'Search...'}" class="search-box">
                <div class="dropdown" style="display: none"></div>
            </div>
        `;
    }
}

customElements.define("search-bar", SearchBar);


