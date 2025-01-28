import $store from '../../store/store.js';
import call from '../../abstracts/call.js';
import { translate } from '../../locale/locale.js';
import { $id, $queryAll, $class } from '../../abstracts/dollars.js'
import WebSocketManager from '../../abstracts/WebSocketManager.js';

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

export function updateConversationBadge(message) {
    const element = $id("chat-view-conversation-card-" +  message.id);
    if(!element){
        console.warn("Conversation card (%s) does not exist. Mostlikely this is not an issue since the actual message will update the badge...", message.id);
        return;
    }
    const seenCouterContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
    seenCouterContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = message.value;
    if (message.value == "0")
        seenCouterContainer.style.display = "none";
    else
        seenCouterContainer.style.display = "flex";
}

export function createMessage(element, prepend = true) {
    // Determine the correct template for the message
    let elementId = "chat-view-sent-message-template";
    let containerId = ".chat-view-sent-message-container";
    if (element.username == "overlords"){
        elementId = "chat-view-overlords-message-template";
        containerId = ".chat-view-overlords-message-container";
    }
    else if (element.userId != $store.fromState("user").id){
        elementId = "chat-view-incoming-message-template";
        containerId = ".chat-view-incoming-message-container";
    }

    let template = $id(elementId).content.cloneNode(true);

    // Set the id of the node to the message id
    let messageContainer = template.querySelector(".chat-view-sent-message-container");
    if(!messageContainer)
        messageContainer = template.querySelector(".chat-view-incoming-message-container");
    if(!messageContainer)
        messageContainer = template.querySelector(".chat-view-overlords-message-container");
    if(!messageContainer || element.id == undefined || element.id == "null")
        console.log("Can't find message container for element. Mostlikely this is not an issue since it is an overlord message");
    else
        messageContainer.id = "message-" + element.id;

    // Set the content of the message
    if (element.userId != $store.fromState("user").id)
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;
    if (element.userId == 1)
        template.querySelector(".chat-view-messages-message-overlords-box").textContent = element.content;
    else
        template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    template.querySelector(".chat-view-messages-message-time-stamp").textContent = moment(element.createdAt).format("h:mma DD-MM-YYYY");
    template.querySelector(containerId).setAttribute("message-id", element.id);

    // Prepend or append the message to the container
    const container = $id("chat-view-messages-container");
    if (prepend) {
        container.prepend(template);
    } else {
        container.appendChild(template);
    }

    // Update the last message id
    const lastMessageId = container.getAttribute("last-message-id");
    if (!lastMessageId || lastMessageId == 0 || element.id < lastMessageId)
        container.setAttribute("last-message-id", element.id);
    console.log("Last message id", lastMessageId);
}

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

export function clickConversationCard(event) {
    // No matter where the user clicks on the card, we want to get the conversation_id
    // Smth like: chat-view-conversation-card-9
    const cardId = event.currentTarget.id;
    // This will than give us the conversation_id in this case 9
    const conversationId = cardId.split('-').pop();
    console.log("Clicked on conversation card with id '%s' so conversationId is: '%s'", cardId, conversationId);
    selectConversation(conversationId);
}

export function createConversationCard(element, highlight = false) {
    const container = $id("chat-view-conversations-container");

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
    if (highlight) {
        card.classList.add("chat-view-conversation-card-highlighted");
    }

    // Set attributes for the card
    card.id = "chat-view-conversation-card-" + element.conversationId;
    card.setAttribute("last-message-time", element.lastUpdate);
    card.querySelector(".chat-view-conversation-card-avatar").src = window.origin + "/media/avatars/" + element.conversationAvatar;
    card.querySelector(".chat-view-conversation-card-username").textContent = element.conversationName;
    card.addEventListener("click", clickConversationCard);


    // Prepend the card to the container
    container.prepend(card);
    // Remove the no-conversations message
    $id("chat-view-conversations-no-converations-found").textContent = "";

    // Handle unseen messages
    updateConversationUnreadCounter(element.conversationId, element.unreadCounter);

    // Trigger the animation after the card is added
    requestAnimationFrame(() => {
        card.classList.remove("chat-view-conversation-card-enter");
        card.classList.add("chat-view-conversation-card-enter-active");
    });

    // Sort the conversations by timestamp
    sortConversationCardsByTimestamp();
}

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

export function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
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
    console.log("Selecting conversation: ", conversationId);
    WebSocketManager.setCurrentConversation(conversationId);
    $id("chat-view-text-field").setAttribute("conversation-id", conversationId);

    // Set url params // TODO: @astein: Not sure if this is the best approach since I don't fully understand the router :D
    history.pushState({}, "Chat", "/chat?id=" + conversationId);

    // Highlight the selected conversation card
    highlightConversationCard(conversationId);

    // Remove old messages
    resetConversationView();

    // Load the conversation header and messages
    await loadMessages(conversationId);

    // Show the chatElements
    $id("chat-view-header-subject-container").style.display = "flex";
    $id("chat-view-header-avatar").style.display = "block";
    $id("chat-view-text-field-container").style.display = "block";

    // Scroll to the bottom
    let scrollContainer = $id("chat-view-messages-container");
    scrollContainer.scrollTop = scrollContainer.scrollHeight + scrollContainer.clientHeight;
}

export function loadMessages(conversationId) {
    const messageContainer = $id("chat-view-messages-container");

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

                    // Update UI with new messages
                    $id("chat-nav-badge").textContent = data.totalUnreadCounter || "";
                    updateConversationUnreadCounter(conversationId, data.conversationUnreadCounter);
                    $id("chat-view-conversation-card-" + conversationId).querySelector(".chat-view-conversation-card-unseen-counter").textContent = data.unreadCounter || "";

                    // Update conversation header
                    //$id("chat-view-header-subject").textContent = "@" + data.conversationName;
                    $id("chat-view-header-subject").innerHTML = `<a href="` + window.origin + "/profile?id=" + data.userId + `" style="text-decoration: none; color: inherit;">@${data.conversationName}</a>`;
                    $id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + data.conversationAvatar;
                    $id("chat-view-header-avatar").setAttribute("user-id", data.userId);
                    $id("chat-view-header-online-icon").src = data.online ? "../assets/onlineIcon.png" : "../assets/offlineIcon.png";

                    // Load messages (prepend as they are in reverse order)
                    for (let element of data.data) {
                        createMessage(element, true);
                    }

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

//export function loadMessages(conversationId, scrollToBottom = false){
//    // Show spinner
//    const messageContainer = $id("chat-view-messages-container");
//    const spinner = createLoadingSpinner();
//    messageContainer.prepend(spinner);
//    const startTime = Date.now();
//
//    // Get the data
//    const lastMsgId = messageContainer.getAttribute("last-message-id");
//    console.log("Loading messages for conversation '%s' with last message id '%s'", conversationId, lastMsgId);
//    call(`chat/load/conversation/${conversationId}/messages/?msgid=${lastMsgId}`, 'PUT')
//    .then(data => {
//        console.log('Data:', data);
//        const elapsedTime = Date.now() - startTime;
//        const delay = Math.max(500 - elapsedTime, 0);
//        setTimeout(() => {
//            spinner.remove();
//            // Update badges
//            $id("chat-nav-badge").textContent = data.totalUnreadCounter || "";
//            updateConversationUnreadCounter(conversationId, data.conversationUnreadCounter);
//            $id("chat-view-conversation-card-" +  conversationId).querySelector(".chat-view-conversation-card-unseen-counter").textContent = data.unreadCounter || "";
//
//            // STEP1: Update about Conversation section
//            // Update Title
//            let title;
//            title = translate("chat", "subject: ") + data.conversationName;
//            $id("chat-view-header-subject").textContent = title;
//
//            // Update online status
//            if (data.online)
//                $id("chat-view-header-online-icon").src = "../assets/onlineIcon.png";
//            else
//                $id("chat-view-header-online-icon").src = "../assets/offlineIcon.png";
//
//            // Update Avatar
//            $id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + data.conversationAvatar;
//            $id("chat-view-header-avatar").setAttribute("user-id", data.userId);
//
//            // Show chat elements
//            $id("chat-view-header-invite-for-game-image").style.display = "block";
//            $id("chat-view-header-subject-container").style.display = "flex";
//            $id("chat-view-header-avatar").style.display = "block";
//            $id("chat-view-text-field-container").style.display = "block";
//
//            // STEP2: Load messages
//            // Note: the messages come in reverse order, so we need to prepend them
//            for (let element of data.data)
//                createMessage(element, true, scrollToBottom);
//
//        }, delay);
//    })
//    .catch(error => {
//        console.error('Error occurred:', error);
//        spinner.remove();
//    })
//}

// This deletes all messages and hides the chatElements
export function resetConversationView(){
    // Hide chatElements
    $id("chat-view-header-subject-container").style.display = "none";
    $id("chat-view-header-avatar").style.display = "none";
    $id("chat-view-text-field-container").style.display = "none";

    // Delete all messages
    let toDelete = $queryAll(".chat-view-sent-message-container, .chat-view-incoming-message-container, .chat-view-overlords-message-container, .spinner-grow")
    for (let element of toDelete)
        element.remove();

    // Unset Attributes
    $id("chat-view-messages-container").setAttribute("last-message-id", 0);
    $id("chat-view-header-avatar").setAttribute("user-id", undefined);
}

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