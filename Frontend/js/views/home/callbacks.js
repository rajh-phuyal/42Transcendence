import { $id } from '../../abstracts/dollars.js';
import router from '../../navigation/router.js';
import call from '../../abstracts/call.js'
import data from './data.js';
import { generateTournamentName } from './methods.js';

function hideModalElements(){
    let modalContent = $id("AI-modal");
    modalContent.style.display = 'none';
    $id("modal-tournament").style.display = 'none';
    $id('home-modal-body').style.backgroundImage = 'none';
}

export function AIModalCallback(){

    let modalElement = $id('home-modal');
    let modalBody = $id('home-modal-body');
    let modalContent = $id("AI-modal")

    hideModalElements();
    modalBody.style.backgroundImage = "url('../../../assets/homeView/AIModal.png')";
    // modalBody.style.height = '90vh';
    // modalBody.style.width = '30vw';

    modalContent.style.display = 'block';
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

}

export function battleModalCallback(){

    let modalElement = $id('home-modal');
    let modalBody = $id('home-modal-body');

    hideModalElements();
    modalBody.style.backgroundImage = "url('../../../assets/homeView/lizardPeopleModal.png')";
    modalBody.style.height = '90vh';
    modalBody.style.width = '30vw';
    modalBody.style.backgroundSize = 'contain'; // Ensure the image covers the whole area background-size: contain
    modalBody.style.backgroundPosition = 'center'; // Center the image
    modalBody.style.backgroundRepeat = 'no-repeat'; // Prevent repeating the image
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
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

    hideModalElements();
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
    let modalBody = $id('home-modal-body');
    let modalElement = $id('home-modal');

    hideModalElements();
    modalBody.style.backgroundImage = "url('../../../assets/homeView/AICard.png')";
    modalBody.style.height = '90vh';
    modalBody.style.width = '30vw';
    modalBody.style.backgroundSize = 'contain'; // Ensure the image covers the whole area background-size: contain
    modalBody.style.backgroundPosition = 'center'; // Center the image
    modalBody.style.backgroundRepeat = 'no-repeat'; // Prevent repeating the image
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}
