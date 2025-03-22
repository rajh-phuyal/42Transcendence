import call from '../../abstracts/call.js';
import { translate } from '../../locale/locale.js';
import { createConversationCard, deleteAllConversationCards, selectConversation, createLoadingSpinner, resetConversationView, loadMessages, resetFilter } from './methods.js';
import router from '../../navigation/router.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import { modalManager } from '../../abstracts/ModalManager.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';

/*
 QUICK EXPLANATION:
    Where is what stored?
    - Selected conversation id:
        .$id("chat-view-text-field").getAttribute("conversation-id")
    - Selected conversation user id:
        .$id("chat-view-header-avatar").getAttribute("user-id");
    - Last message id of currenty loaded conversation:
        .$id("chat-view-messages-container").getAttribute("last-message-id");
*/
export default {
    attributes: {
    },

    methods: {
        setTranslations() {
            this.domManip.$id("chat-view-searchbar").placeholder = translate("chat", "filterConversations");
            this.domManip.$id("chat-room-heading").innerText = translate("chat", "ChatRoom");
        },

        // THE LISTENERS
        // -------------------------------------------
        // This is the Event Listener for the infinite scroll
        scrollListener(){
            const container = this.domManip.$id("chat-view-messages-container");
            if(!container){
                console.error("No chat-view-messages-container found. Unable to add infinite scroll.");
                return ;
            }
            if (container.scrollTop === 0) {
                const conversationId = this.domManip.$id("chat-view-text-field").getAttribute("conversation-id");
                if(conversationId){
                    const container = this.domManip.$id("chat-view-messages-container");
                    const lastMessageId = container.getAttribute("last-message-id");
                    const lastMessageContainer = this.domManip.$id("message-" + lastMessageId);
                    loadMessages(conversationId).then(() => {
                        if (lastMessageContainer){
                            lastMessageContainer.scrollIntoView({
                                behavior: "instant",
                                block: "start",
                            });
                        }
                    }).catch(error => {
                        console.error("Failed to load messages during infinite scroll:", error);
                    });
                }
                else
                    console.error("handleScroll: No conversation selected. Unable to load older messages.");
            }
        },

        // This is the Event Listener for the avatar click
        clickAvatarListener() {
            const avatar = this.domManip.$id("chat-view-header-avatar");
            if(!avatar){
                console.error("No chat-view-header-avatar found. Unable to add avatar click event listener.");
                return ;
            }

            const userId = avatar.getAttribute("user-id");
            if (userId) {
                router(`/profile`, { id: userId });
            } else {
                console.warn("No conversation selected. Unable to navigate to profile.");
            }
        },

        // This is the Event Listener for the search bar typing
        searchBarTypeListener(event) {
            const searchBar = this.domManip.$id("chat-view-searchbar");
            const conversationsContainer = this.domManip.$id("chat-view-conversations-container");

            if (!searchBar || !conversationsContainer) {
                console.error("No search bar or conversations container found. Unable to add search event listener.");
                return ;
            }

            const query = searchBar.value.toLowerCase();
            const conversationCards = conversationsContainer.querySelectorAll(".chat-view-conversation-card");

            conversationCards.forEach((card) => {
                const username = card.querySelector(".chat-view-conversation-card-username").textContent.toLowerCase();
                if (username.includes(query)) {
                    card.style.display = "flex"; // Show matching cards
                } else {
                    card.style.display = "none"; // Hide non-matching cards
                }
            });
        },

        // This is the Event Listener for the search bar keydown (Enter, Escape)
        searchBarKeydownListener(event) {
            const searchBar = this.domManip.$id("chat-view-searchbar");
            const conversationsContainer = this.domManip.$id("chat-view-conversations-container");

            if (!searchBar || !conversationsContainer) {
                console.error("No search bar or conversations container found. Unable to add search event listener.");
                return ;
            }

            if (event.key === "Escape") {
                // ESC clears the search bar
                resetFilter();
            } else if (event.key === "Enter") {
            // ENTER selects the first visible card
                const visibleCards = Array.from(conversationsContainer.querySelectorAll(".chat-view-conversation-card"))
                    .filter((card) => card.style.display !== "none"); // Only include visible cards

                if (visibleCards.length > 0) {
                    visibleCards[0].click(); // Simulate a click on the first filtered card
                    searchBar.value = ""; // Clear the search bar

                    // Show all cards again
                    const allCards = conversationsContainer.querySelectorAll(".chat-view-conversation-card");
                    allCards.forEach((card) => {
                        card.style.display = "flex";
                    });
                }
            }
        },

        // This is the Event Listener for the mentions (@user, #game, #tournament)
        messageMeantionListener(event) {
            const mention = event.target.closest(".mention-user");
            const tournament = event.target.closest(".mention-tournament");
            const game = event.target.closest(".mention-game");

            // Check if a mention USER was clicked
            if (mention) {
                const userId = mention.getAttribute("data-userid");
                if (userId)
                    router(`/profile`, { id: userId });
                else
                    console.warn("Mention clicked but no user ID found.");
            }

            // Check if a mention TOURNAMENT was clicked
            if (tournament) {
                const tournamentId = tournament.getAttribute("data-tournamentid");
                if (tournamentId)
                    router(`/tournament`, { id: tournamentId });
                else
                    console.warn("Mention clicked but no tournament ID found.");
            }

            // Check if a mention GAME was clicked
            if (game) {
                const gameId = game.getAttribute("data-gameid");
                if(gameId)
                    router(`/game`, { id: gameId });
                else
                    console.warn("Mention clicked but no game ID found.");
            }
        },

        eyeListener(event){
            let backgroundImage = this.domManip.$id("chat-view-eye-background");
            let pupil = this.domManip.$id("chat-view-eye-pupil");
            const rect = backgroundImage.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const relativeX = Math.round(event.clientX - centerX);
            const relativeY = Math.round(event.clientY - centerY);
            const maxMoveX = backgroundImage.width * 0.25;
            const maxMoveY = backgroundImage.height * 0.2;
            let percentageMoveX = 0
            let percentageMoveY = 0
            if (relativeX > 0)
                percentageMoveX = (relativeX / (window.innerWidth - centerX));
            else
                percentageMoveX = (relativeX / centerX);
            if (relativeY > 0)
                percentageMoveY = (relativeY / (window.innerHeight - centerY));
            else
                percentageMoveY = (relativeY / centerY);
            const moveX = percentageMoveX * maxMoveX;
            const moveY = percentageMoveY * maxMoveY;
            pupil.style.transform = `translate(-50%, -50%) translate(${moveX}px, ${moveY}px)`;
        },

        // This will be called only once by afterDomInsertion to initalize the cards via REST API
        async loadConversations() {
            const conversationsContainer = this.domManip.$id('chat-view-conversations-container');

            if(!conversationsContainer){
                console.error("No chat-view-conversations-container found. Unable to load conversations.");
                return Promise.resolve();
            }

            // To avoid multiple calls at the same time
            if(conversationsContainer.getAttribute("loading") == "true"){
                console.warn("Already loading conversations. Please wait.");
                return Promise.resolve();
            }
            conversationsContainer.setAttribute("loading", "true");

            // Remove all conversation cards
            deleteAllConversationCards();

            // Show Spinner
            const spinner = createLoadingSpinner();
            conversationsContainer.prepend(spinner);
            const startTime = Date.now();

            // Load the conversations
            return call('chat/load/conversations/', 'GET')
                .then(data => {
                    const elapsedTime = Date.now() - startTime;
                    const delay = Math.max(200 - elapsedTime, 0);

                    // Return a promise to wait for the spinner and the api call
                    return new Promise(resolve => {
                        setTimeout(() => {
                            spinner.remove();

                            // Check if there are any messages
                            if (!data.data) {
                                this.domManip.$id("chat-view-conversations-no-converations-found").textContent = data.message;
                                conversationsContainer.setAttribute("loading", "false");
                                resolve();
                                return;
                            }

                            // Create the conversation cards
                            for (let element of data.data) {
                                createConversationCard(element, false);
                            }

                            // Restore the loading attribute and resolve the promise
                            conversationsContainer.setAttribute("loading", "false");
                            resolve();
                        }, delay);
                    });
                })
                .catch(error => {
                    spinner.remove();
                    conversationsContainer.setAttribute("loading", "false");
                    console.error('Error occurred:', error);
                });
        },
    },

    hooks: {
        async beforeRouteEnter() {
        },

        beforeRouteLeave() {
            modalManager.off("chat-view-btn-create-game", "modal-create-game");
            // Remove all conversations
            deleteAllConversationCards();
            // Remove all messages
            resetConversationView();
            // Remove the attributes which the createGameModal uses
            const view = this.domManip.$id("router-view");
            view.removeAttribute("data-user-id");
            view.removeAttribute("data-user-username");
            view.removeAttribute("data-user-avatar");
        },

        beforeDomInsertion() {
        },

        async afterDomInsertion() {
            // Set translations
            this.setTranslations();

            // Init everything conversation related (right side of view)
            resetConversationView();

            // Init all variables we use later on:
            this.domManip.$id("chat-view-text-field").setAttribute("conversation-id", undefined);
            this.domManip.$id('chat-view-conversations-container').setAttribute("loading", "false");
            this.domManip.$id("chat-view-messages-container").setAttribute("loading", "false");

            // Load the conversations
            this.loadConversations()
                .then(() => {
                    if (this.routeParams?.id){
                        // Check if is is number
                        if (isNaN(this.routeParams.id)){
                            console.warn("Invalid conversation id '%s' from routeParams?.id will be ignored!", this.routeParams.id);
                            return ;
                        }
                        selectConversation(this.routeParams.id);
                    }
                })
                .catch(error => {
                    console.error("Error loading conversations:", error);
                });

            // Add event listeners
            // - for search bar
            EventListenerManager.linkEventListener("chat-view-searchbar", "chat", "input", this.searchBarTypeListener);
            EventListenerManager.linkEventListener("chat-view-searchbar", "chat", "keydown", this.searchBarKeydownListener);
            // - for infinite scroll
            EventListenerManager.linkEventListener("chat-view-messages-container", "chat", "scroll", this.scrollListener);
            // - for avatar click
            const avatar = this.domManip.$id("chat-view-header-avatar");
            avatar.style.cursor = "pointer";
            EventListenerManager.linkEventListener("chat-view-header-avatar", "chat", "click", this.clickAvatarListener);
            // - for mentions
            EventListenerManager.linkEventListener("chat-view-messages-container", "chat", "click", this.messageMeantionListener);
            // - for eye
            EventListenerManager.linkEventListener("barely-a-body", "chat", "mousemove", this.eyeListener);
            // Add modal event listener
            modalManager.on("chat-view-btn-create-game", "modal-create-game");
        },
    },
};
