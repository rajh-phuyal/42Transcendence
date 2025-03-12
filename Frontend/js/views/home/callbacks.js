import { $id } from '../../abstracts/dollars.js';
import router from '../../navigation/router.js';
import call from '../../abstracts/call.js'
import data from './data.js';
import { generateTournamentName } from './methods.js';
import { modalManager } from '../../abstracts/ModalManager.js';

export function AIModalCallback(){
    // Set the opponent to AI
    const view = $id("router-view");
    view.setAttribute("data-user-id", "2");
    view.setAttribute("data-user-username", "ai");                                     // TODO: maybe this should be saved somewhere else as a constant
    view.setAttribute("data-user-avatar", "670eb5bf-72cb-45bc-b17c-9fcf029b9197.png"); // TODO: maybe this should be saved somewhere else as a constant
    modalManager.openModal("modal-create-game");
}

export function battleModalCallback(){
    // Remove the attributes from the view so that the user can select a friend in the modal
    const view = $id("router-view");
    view.removeAttribute("data-user-id");
    view.removeAttribute("data-user-username");
    view.removeAttribute("data-user-avatar");
    modalManager.openModal("modal-create-game");
}


// TODO: return a boolean and treat the data inside the call function
function checkEnrolement() {
    call('tournament/enrolment/','GET').then(data => {
        console.log("enrolement:", data);
        return data;
    }).error( error => {
        console.log(error);
        return error; // TODO: maybe return a "error"
    })
}

function createTournamentCard(element) {
    const template = $id("modal-tournament-tournament-template").content.cloneNode(true);

    template.querySelector("modal-tournament-tournament-name").textContent = element.name; // Check if this is the keyword name

}

function createJoinTournamentList() {

    call('tournament/to-join/','GET').then(data => {
        const listContainer = $id("modal-tournament-tournament-list");

        // loop through the tournaments call the createTournamentCard function

    })

}

export function tournamentModalCallback(){
    let modalElement = $id('home-modal');
    let modalBody = $id('home-modal-body');


    // modalBody.style.backgroundImage = "url('../../../assets/homeView/bigfootModal2.png')";
    modalBody.style.height = '90vh';
    modalBody.style.width = '80vw';
    // modalBody.style.backgroundSize = 'contain'; // Ensure the image covers the whole area background-size: contain
    // modalBody.style.backgroundPosition = 'center'; // Center the image
    // modalBody.style.backgroundRepeat = 'no-repeat'; // Prevent repeating the image
    $id("modal-tournament").style.display = 'flex';
    const modal = new bootstrap.Modal(modalElement);
    // Adding a "random name" to the tournament name input. That needs to be
    // done so that the client can create a tournament without having to type
    // a name. This "fast button" is mandatory from subject
    $id("modal-tournament-create-form-name-container-input").value = generateTournamentName();
    modal.show();
}

export function chatRoomModalCallback(){
    router("/chat");
}

export function leaderboardModalCallback(){
    modalManager.openModal("modal-leaderboard");
}
