import $store from '../../store/store.js';
import call from '../../abstracts/call.js';
import { $id, $queryAll, $on, $off, $class, $addClass } from '../../abstracts/dollars.js'
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import { translate } from '../../locale/locale.js';

// -----------------------------------------------------------------------------
// WEBSOCKET MANAGER TRIGGERS
// -----------------------------------------------------------------------------

// This function will be called by the WebSocketManager when a new message is received via the websocket
export function processIncomingWsChatMessage(message) {
    // Update the conversation card attribute and sort the cards
    const conversationCard = $id("chat-view-conversation-card-" + message.conversationId);
    if (conversationCard) {
        conversationCard.setAttribute("last-message-time", message.createdAt);
        sortConversationCardsByTimestamp();
    }
    // The conversation card is already selected so we can just add the message
    const currentConversationId = $id("chat-view-text-field").getAttribute("conversation-id");
    if (currentConversationId && currentConversationId == message.conversationId) {
        createMessage(message, false);
        // Scroll to the bottom
        let scrollContainer = $id("chat-view-messages-container");
        scrollContainer.scrollTop = scrollContainer.scrollHeight + scrollContainer.clientHeight;

        // send seen message if it is not ur own message
        if (message.userId != $store.fromState("user").id)
            WebSocketManager.sendMessage({messageType: "seen", conversationId: message.conversationId});
        return ;
    }
}

// This will be called by:
//    - WebsocketManager if updateBadge messaage is received
//    - by createConversationCard to initialize the badge
export function updateConversationBadge(conversationId, value) {
    const element = $id("chat-view-conversation-card-" +  conversationId);
    if(!element){
        console.warn("Conversation card (%s) does not exist. Mostlikely this is not an issue since the actual message will update the badge...", conversationId);
        return;
    }
    const seenCouterContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
    seenCouterContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = value;
    if (value == 0)
        seenCouterContainer.style.display = "none";
    else
        seenCouterContainer.style.display = "flex";
}

// -----------------------------------------------------------------------------
// CONVERSATION CARDS STUFF
// -----------------------------------------------------------------------------

// This will be called either by the REST API or the WebSocketManager
// It creads a card, adds it to the container and sorts the cards
export function createConversationCard(element, highlight = false) {
    const container = $id("chat-view-conversations-container");
    if (!container) {
        console.error("Conversations container not found.");
        return;
    }

    // Check if card already exists
    if ($id("chat-view-conversation-card-" + element.conversationId)) {
        console.warn("Conversation card already exists:", element.conversationId);
        return;
    }

    // Clone the template
    const conversation = $id("chat-view-conversation-card-template").content.cloneNode(true);
    const card = conversation.querySelector(".chat-view-conversation-card");

    // Add the 'enter' class for animation
    card.classList.add("chat-view-conversation-card-enter");

    // Highlight the card if needed
    if (highlight)
        card.classList.add("chat-view-conversation-card-highlighted");

    // Set attributes for the card
    card.id = "chat-view-conversation-card-" + element.conversationId;
    card.setAttribute("last-message-time", element.lastUpdate);
    card.querySelector(".chat-view-conversation-card-avatar").src = window.origin + "/media/avatars/" + element.conversationAvatar;
    card.querySelector(".chat-view-conversation-card-username").textContent = element.conversationName;
    $on(card, "click", coversationCardClickListener);

    // Prepend the card to the container
    container.prepend(card);

    // Remove the no-conversations message
    $id("chat-view-conversations-no-converations-found").textContent = "";

    // Handle unseen messages
    updateConversationBadge(element.conversationId, element.unreadCounter);

    // Sort the conversations by timestamp
    sortConversationCardsByTimestamp();

    // Trigger the animation after the card is added
    requestAnimationFrame(() => {
        card.classList.remove("chat-view-conversation-card-enter");
        card.classList.add("chat-view-conversation-card-enter-active");
    });
}

// The listener for the conversation card wich will detemermine the
// conversation id and call the selectConversation function
export function coversationCardClickListener(event) {
    // No matter where the user clicks on the card, we want to get the conversation_id
    // Smth like: chat-view-conversation-card-9
    const cardId = event.currentTarget.id;
    // This will than give us the conversation_id in this case 9
    const conversationId = cardId.split('-').pop();
    // Clear the searchbar
    resetFilter();
    // Update the selected conversation
    selectConversation(conversationId);
}

// Only called by selectConversation to visaualize the selected conversation
export function highlightConversationCard(conversationId) {
    // Remove highlighting from all cards
    const highlightedCards = $queryAll(".chat-view-conversation-card-highlighted");
    for (let card of highlightedCards) {
        card.classList.remove("chat-view-conversation-card-highlighted");
        card.classList.add("chat-view-conversation-card");
    }

   // Find the specific card to highlight
   const targetCard = $id("chat-view-conversation-card-" + conversationId);
   if (targetCard) {
        targetCard.classList.add("chat-view-conversation-card-highlighted");
        // Scroll to the highlighted card
        targetCard.scrollIntoView({
            behavior: "smooth",
            block: "nearest",
        });
   }
}

// Sort the conversation cards by the `last-message-time` attribute
export function sortConversationCardsByTimestamp() {
    const container = $id("chat-view-conversations-container");

    // Convert the children (conversation cards) to an array
    const cards = Array.from(container.children);

    // Sort the cards by the `last-message-time` attribute (newest first)
    cards.sort((a, b) => {
        const timestampA = new Date(a.getAttribute("last-message-time"));
        const timestampB = new Date(b.getAttribute("last-message-time"));
        return timestampB - timestampA;
    });

    // Re-append sorted cards to the container (this reorders them in the DOM)
    cards.forEach((card) => container.appendChild(card));
}

// Called before loading or before leaving the chat view
export function deleteAllConversationCards() {
    const cards = $queryAll(".chat-view-conversation-card");
    for (let card of cards) {
        $off(card, "click", coversationCardClickListener);
        card.remove();
    }
}

// Resets the filter
export function resetFilter() {
    const conversationsContainer = $id("chat-view-conversations-container");
    const searchBar = $id("chat-view-searchbar");
    searchBar.value = "";
    const conversationCards = conversationsContainer.querySelectorAll(".chat-view-conversation-card");
    conversationCards.forEach((card) => {
        card.style.display = "flex"; // Show all cards
    });
}

// -----------------------------------------------------------------------------
// MESSAGE STUFF
// -----------------------------------------------------------------------------

// This function will be called:
//    - by the WebSocketManager when a new message is received via the websocket
//    - by the REST API when selecting a conversation
export function createMessage(element, prepend = true) {
    // Determine the correct template for the message
    let elementId = "chat-view-message-template";
    let containerId = ".chat-view-message-container";
    // Clone the template
    let template = $id(elementId).content.cloneNode(true);

    // Add the right styling class for container
    let messageContainer = template.querySelector(".chat-view-message-container");
    if (element.username == "overlords")
        messageContainer.classList.add("chat-view-message-container-overlords");
    else if (element.userId == $store.fromState("user").id)
        messageContainer.classList.add("chat-view-message-container-outgoing");
    else
        messageContainer.classList.add("chat-view-message-container-incoming");

    // Add the right styling class for box
    if (element.username == "overlords")
        template.querySelector(".chat-view-message-box").classList.add("chat-view-message-box-overlords");
    else if (element.userId != $store.fromState("user").id)
        template.querySelector(".chat-view-message-box").classList.add("chat-view-message-box-outgoing");
    else
        template.querySelector(".chat-view-message-box").classList.add("chat-view-message-box-incoming");

    // Set the id of the node to the message id
    messageContainer = template.querySelector(".chat-view-message-container");
    if(!messageContainer || element.id == undefined || element.id == "null")
        console.log("Can't find message container for element. Mostlikely this is not an issue since it is an overlord message");
    else
        messageContainer.id = "message-" + element.id;
    // Set username
    template.querySelector(".chat-view-message-sender").textContent = element.username;
    template.querySelector(".chat-view-message-sender").setAttribute("data-userid", element.userId);

    // PARSE THE CONTENT
    // Match @<username>@<userid>@ pattern
    let parsedContent = element.content;
    if (element.content != null) {
        parsedContent = element.content.replace(
            /@([^@]+)@([^@]+)@/g,
            `<span class="mention-user" data-userid="$2">@$1</span>`
        );
        // Match #T#<tournamentName>#<tournamentId># pattern
        parsedContent = parsedContent.replace(
            /#T#([^#]+)#([^#]+)#/g,
            '<span class="mention-tournament" data-tournamentid="$2">#$1</span>'
        );
        // Match #G#<gameId># pattern
        parsedContent = parsedContent.replace(
            /#G#([^#]+)#/g,
            '<span class="mention-game" data-gameid="$1">#$1</span>'
        );
    }

    // Set the content of the message
    template.querySelector(".chat-view-message-box").innerHTML = parsedContent;

    // Set the timestamp and the node id
    template.querySelector(".chat-view-message-timestamp").textContent = moment(element.createdAt).format("h:mma DD-MM-YYYY");
    template.querySelector(containerId).setAttribute("message-id", element.id);

    // Prepend or append the message to the container
    const container = $id("chat-view-messages-container");
    if (prepend)
        container.prepend(template);
    else {
        // If the help message is already there, we need to insert the message before it
        const lastChild = container.lastElementChild;
        if (!lastChild || !lastChild.classList.contains("chat-view-help-message-container"))
            container.appendChild(template);
        else
            container.insertBefore(template, lastChild);
    }

    // Update the last message id (to be able to know where the next scroll load should start)
    const lastMessageId = container.getAttribute("last-message-id");
    if (!lastMessageId || lastMessageId == 0 || element.id < lastMessageId)
        container.setAttribute("last-message-id", element.id);
}

/* This is the main function for selecting a conversation.
    It will be called from:
        - client clicking on a conversation card
        - route param in the URL (e.g /chat?id=9)
    This function will then:
        - set the conversation id to other functions where we need them: TODO: not sure if this is a smart approach
        - clear the current conversation
        - load the conversation from the server
        - set the info section about the conversation (chat name, avatar, etc)
        - load the messages and display them
        - show the chatElements like the input box, etc
*/
export async function selectConversation(conversationId){
    // Set variables
    $id("chat-view-text-field").setAttribute("conversation-id", conversationId);

    // Set url params // TODO: @astein: Not sure if this is the best approach since I don't fully understand the router :D
    history.pushState({}, "Chat", "/chat?id=" + conversationId);

    // Remove old messages
    resetConversationView();

    // Highlight the selected conversation card
    highlightConversationCard(conversationId);

    // Load the conversation header and messages
    await loadMessages(conversationId);

    // Show the chatElements
    $id("chat-view-details").style.display = "flex";
    $id("chat-view-details-img").style.display = "flex";
    let inputField = $id("chat-view-text-field");
    inputField.style.display = "flex";
    console.log("Draft:", $id("chat-view-conversation-card-" + conversationId).getAttribute("message-draft"));
    inputField.setInput($id("chat-view-conversation-card-" + conversationId).getAttribute("message-draft") || "");
    inputField.focus();

    // Scroll to the bottom
    let scrollContainer = $id("chat-view-messages-container");
    scrollContainer.scrollTop = scrollContainer.scrollHeight + scrollContainer.clientHeight;
}

// Loading messages from the server and adding it to the chat view
// Called by:
//    - selectConversation (via click on card or route param)
//    - scrollListener (via scroll uo in conversation)
export function loadMessages(conversationId) {
    const messageContainer = $id("chat-view-messages-container");

    if(!messageContainer){
        console.error("Message container not found.");
        return;
    }

    // Prevent duplicate requests
    if (messageContainer.getAttribute("loading") === "true") {
        console.warn("Messages are already loading. Please wait.");
        return Promise.resolve();
    }

    // Set loading state
    messageContainer.setAttribute("loading", "true");

    // Show spinner
    const spinner = createLoadingSpinner();
    messageContainer.prepend(spinner);
    const startTime = Date.now();

    // Return a Promise for better flow control
    return call(`chat/load/conversation/${conversationId}/messages/?msgid=${messageContainer.getAttribute("last-message-id")}`, 'PUT')
        .then(data => {
            const elapsedTime = Date.now() - startTime;
            const delay = Math.max(200 - elapsedTime, 0);
            return new Promise(resolve => {
                setTimeout(() => {
                    spinner.remove();
                    // Update conversation header
                    $id("chat-view-header-subject").innerHTML = `<a href="` + window.origin + "/profile?id=" + data.userId + `" style="text-decoration: none; color: inherit;">${translate("chat", "subject") + "<br>" + data.conversationName}</a>`;
                    $id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + data.conversationAvatar;
                    $id("chat-view-header-avatar").setAttribute("user-id", data.userId);
                    $id("chat-view-header-online-icon").src = data.online ? "../assets/onlineIcon.png" : "../assets/offlineIcon.png";
                    // Load messages (prepend as they are in reverse order)
                    for (let element of data.data)
                        createMessage(element, true);

                    // Reset loading state
                    messageContainer.setAttribute("loading", "false");

                    resolve(); // Indicate that messages are loaded
                }, delay);
            });
        })
        .catch(error => {
            console.error("Error occurred while loading messages:", error);
            spinner.remove();
            messageContainer.setAttribute("loading", "false"); // Reset loading state
        });
}

// -----------------------------------------------------------------------------
// HELPERS STUFF
// -----------------------------------------------------------------------------

// This deletes all messages and hides the chatElements (right side of the chat view)
export function resetConversationView(){
    // Hide chatElements
    $id("chat-view-details").style.display = "none";
    $id("chat-view-details-img").style.display = "none";
    // Store input as attribute
    let inputField = $id("chat-view-text-field");
    let inputValue = inputField.getInput().trim();
    if (inputValue) {
        const highlightedCards = $queryAll(".chat-view-conversation-card-highlighted");
        if (highlightedCards && highlightedCards.length > 0)
            highlightedCards[0].setAttribute("message-draft", inputValue);
    }
    inputField.setEnabled(false);
    inputField.style.display = "none";
    // Delete all messages
    let toDelete = $queryAll(".chat-view-message-container, .spinner-grow")
    for (let element of toDelete)
        element.remove();
    // Unset Attributes
    $id("chat-view-messages-container").setAttribute("last-message-id", 0);
    $id("chat-view-header-avatar").setAttribute("user-id", undefined);
}

// Creates and returns a bootstrap spinner element
export function createLoadingSpinner() {
    const spinnerContainer = document.createElement("div");
    spinnerContainer.style.display = "flex";
    spinnerContainer.style.justifyContent = "center";
    spinnerContainer.style.width = "100%";
    spinnerContainer.style.marginTop = "1rem";
    spinnerContainer.style.marginBottom = "1rem";

    const spinner = document.createElement("div");
    spinner.className = "spinner-grow";
    spinner.innerHTML = `<div class="spinner-grow" role="status"><span class="sr-only"></span></div>`;
    spinnerContainer.appendChild(spinner);
    return spinnerContainer;
}































export function updateConversationUnreadCounter(conversationId, value) {
    let element = $id("chat-view-conversation-card-" +  conversationId);
    let unseenContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
    if (value == 0)
        unseenContainer.style.display = "none";
    else {
        unseenContainer.style = "flex";
        unseenContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = value;
    }
}

// When a user inputs a chat message, this function will be called to update
// the helper text for message cmds like /F
export function createHelpMessage(input){
    // Check if input supports a help message
    const cmds = ["/G", "/F", "/B", "/U"];
    input = input.toUpperCase();
    let htmlContent = ""
    if (input == "/" || cmds.some(prefix => input.startsWith(prefix))) {
        // We need more options for /G and /F
        if(input.startsWith("/G")) {
            // Count the typed "," to determine the step of the game creation
            const commaCount = input.split(",").length - 1;
            console.log("Comma count:", commaCount);
            if (commaCount < 2)
                htmlContent = translate("chat", "helpMessage/G0");
            else if (commaCount == 2) {
                // check if it ends on yes or no
                if (input.endsWith("YES") || input.endsWith("NO"))
                    htmlContent = translate("chat", "helpMessage/G3");
                else
                    htmlContent = translate("chat", "helpMessage/G2");
            }
        } else if(input.startsWith("/F")) {
            if (input.length == 2)
                htmlContent = translate("chat", "helpMessage/F");
            else if (input.length == 3)
                htmlContent = translate("chat", "helpMessage/F1");
        } else
            htmlContent = translate("chat", "helpMessage" + input)
    } else {
        if (input.includes("@"))
            htmlContent += translate("chat", "helpMessage/mention-username");
        if (input.includes("#"))
            htmlContent += translate("chat", "helpMessage/mention-tournament-game");
    }





    updateHelpMessage(htmlContent);
}

export function updateHelpMessage(htmlContent="") {
    let helpContainer = $id("message-help");
    if (htmlContent){
        // Show the help message
        if (!helpContainer){
            // Create node from template
            let template = $id("chat-view-help-message-template").content.cloneNode(true);
            helpContainer = template.querySelector(".chat-view-help-message-container");
            helpContainer.id = "message-help";
            // Append it to chat view
            const container = $id("chat-view-messages-container");
            container.appendChild(helpContainer);
        }
        helpContainer.innerHTML = htmlContent;
        // Scroll to bottom
        let scrollContainer = $id("chat-view-messages-container");
        scrollContainer.scrollTop = scrollContainer.scrollHeight + scrollContainer.clientHeight;
    } else {
        // Hide the help message
        if (helpContainer)
            helpContainer.remove();
    }
}

