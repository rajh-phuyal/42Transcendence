import { $id } from '../../abstracts/dollars.js';
import router from '../../navigation/router.js';

function hideModalElements(){
    let modalContent = $id("AI-modal");
    modalContent.style.display = 'none';
    $id("tournament-modal").style.display = 'none';
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

export function tournamentModalCallback(){
    console.log("here");
    let modalElement = $id('home-modal');
    let modalBody = $id('home-modal-body');
    
    hideModalElements();
    // modalBody.style.backgroundImage = "url('../../../assets/homeView/bigfootModal2.png')";
    modalBody.style.height = '90vh';
    modalBody.style.width = '80vw';
    // modalBody.style.backgroundSize = 'contain'; // Ensure the image covers the whole area background-size: contain
    // modalBody.style.backgroundPosition = 'center'; // Center the image
    // modalBody.style.backgroundRepeat = 'no-repeat'; // Prevent repeating the image
    $id("tournament-modal").style.display = 'flex';
    const modal = new bootstrap.Modal(modalElement);
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