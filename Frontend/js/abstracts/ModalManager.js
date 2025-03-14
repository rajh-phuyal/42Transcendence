import { $id, $on, $off, $class } from './dollars.js';
import { objectToBind } from '../navigation/router.js';

const modalFolders = [
    ["modal-new-conversation", "newConversation"],
    ["modal-edit-friendship", "editFriendship"],
    ["modal-edit-profile", "editProfile"],
    ["modal-friends-list", "friendsList"],
    ["modal-create-game", "createGame"],
    ["modal-game-history", "gameHistory"],
    ["modal-template", "template"],
    ["modal-tournament", "tournament"],
    ["modal-template-image", "templateImage"],
];
export default class ModalManager {
    static instance = null;     // Instance of the singleton
    static modalInstances = {}; // Here we store both: modal instances & their bound event listeners ( to be able to remove them later )

    /* For the singleton export */
    static getInstance() {
        if (!ModalManager.instance) {
            ModalManager.instance = new ModalManager();
        }
        return ModalManager.instance;
    }

    /* Helpers to convert between modal names and folder names
    ========================================================================= */
    static idToFolderNameStatic(modalName) {
        const result = modalFolders.find(([modal, _]) => modal === modalName);
        return result ? result[1] : null; // Return filename or null if not found
    }
    idToFolderName(modalName) {
        const result = modalFolders.find(([modal, _]) => modal === modalName);
        return result ? result[1] : null; // Return filename or null if not found
    }

    folderNameToId(folderName) {
        const result = modalFolders.find(([_, folder]) => folder === folderName);
        return result ? result[0] : null; // Return modal ID or null if not found
    }

    /* HELPERS TO SETUP A SINGLE MODAL
    ========================================================================= */

    /* Used by setupModal to load the hooks for a modal */
    static async loadModalHooks(modalId) {
        const folderName = ModalManager.idToFolderNameStatic(modalId);
        if (!folderName) {
            console.warn(`ModalManager: Couldn't find folder name for modal: ${modalId}`);
            return null;
        }
        const path = `../modals/${folderName}/configs.js`;
        return await import(path)
            .then(conf => conf.default)
            .catch(() => {
                console.warn(`Couldn't load hooks for modal: ${modalId}`);
                return null;
            });
    }

    async setupModal(modalId) {
        console.log(`ModalManager: Setting up modal: ${modalId}`);
        const modalElement = $id(modalId);
        if (!modalElement) {
            console.warn(`ModalManager: Modal element not found: ${modalId}`);
            return;
        }

        // Create a new instance of the modala and store it
        const instance = new bootstrap.Modal(modalElement);
        ModalManager.modalInstances[modalId] = {
            instance: instance,
            openCallback: null,
        };

        // Load the hooks for the modal
        const modalHooks = await ModalManager.loadModalHooks(modalId);
        if (!modalHooks) return; // Error msg will be already displayed in the loadModalHooks function
        const modalConfig = objectToBind(modalHooks);

        // Prevent duplicate event listeners by removing them first
        $off(modalElement, 'show.bs.modal');
        $off(modalElement, 'hidden.bs.modal');
        // Attach Bootstrap event listeners // TODO: dont use annonymos function
        $on(modalElement, 'show.bs.modal', async () => {
            console.log(`ModalManager: Opening modal: ${modalId}`);
            if (modalHooks.hooks.beforeOpen) {
                await modalHooks.hooks.beforeOpen.bind(modalConfig)();
            } else
                console.warn(`ModalManager: Couldn't find the 'beforeOpen' function for modal: ${modalId}`);
        });
        $on(modalElement, 'hidden.bs.modal', async () => {
            console.log(`ModalManager: Closing modal: ${modalId}`);
            if (modalHooks.hooks.afterClose)
                await modalHooks.hooks.afterClose.bind(modalConfig)();
            else
                console.warn(`ModalManager: Couldn't find the 'afterClose' function for modal: ${modalId}`);
        });
    }

    /* FUNCTIONS FOR THE ROUTER
    ========================================================================= */

    /*
    The idea is that the router calls this function after inserting the html for the modals
    So the modal manager can loop trough the modal nodes and set up the modals which means:
        - create the bootstrap modal instance
        - set up the event listeners (open, close)
    */
    async setupAllModalsForView() {
        const modalsContainer = $id("modal-view");
        // Loop through the modals and set them up
        for (const modal of modalsContainer.children) {
            if (modal.tagName === "DIV") { // To prevent setting up the style tag
                console.log("setupAllModalsForView: Seting up:", modal.id);
                await this.setupModal(modal.id);
            }
        }
    }

    /*
    Before changing route this function will be called it:
      - removes all event listeners (open, close)
      - removes all event listeners from the buttons that open the modals
      - destroys all modal instances
      - removes all modals from the DOM
    */
    destroyAllModals() {
        console.log("ModalManager: Destroying all loaded modals");
        Object.keys(ModalManager.modalInstances).forEach(modalId => {
            const modalElement = $id(modalId);
            // Deal wih the instance
            const modalInstance = ModalManager.modalInstances[modalId].instance;
            if (modalInstance) {
                // Remove all Bootstrap event listeners
                if (modalElement) {
                    $off(modalElement, 'show.bs.modal');
                    $off(modalElement, 'hidden.bs.modal');
                }
                // Remove all open modal event listeners (Deal with the openCallback)
                this.off(modalId);
                modalInstance.dispose();
                ModalManager.modalInstances[modalId].instance = null;
            }
            delete ModalManager.modalInstances[modalId];
            // Deal with the DOM
            if (modalElement && modalElement.parentNode) {
                modalElement.parentNode.removeChild(modalElement);
            }
        });
    }

    /* OPENING A MODAL
    =========================================================================
    There are two ways how to open a modal:
       - for view home:     openModal()     -> This will open the modal
       - for other views:   on()            -> This will add an event listener to the button which opens the modal
    */

    /* This can be used everywhere like modalManager.openModal("modal-create-game") */
    async openModal(modalId) {
        if(!modalId) {
            console.warn("ModalManager: need argument modalId");
            return;
        }
        let modalElement = $id(modalId);
        if (!modalElement) {
            console.warn(`ModalManager: openModal: Modal element not found: ${modalId}`);
            return;
        }
        await this.tryToShowModal(modalId);
    }

    /* This is the callback function for on() which will be stored in the ModalManager.modalInstances.openCallback */
    async openModalCallback(event) {
        const modalId = event.target.getAttribute("target-modal-id");
        if(!modalId) {
            console.warn("ModalManager: openModalCallback: No modal id found in the event target");
            return;
        }
        let modalElement = $id(modalId);
        if (!modalElement) {
            console.warn(`ModalManager: openModalCallback: Modal element not found: ${modalId}`);
            return;
        }
        await this.tryToShowModal(modalId);
    }

    /* This can be used from a configs.js of a view to open a modal when a button is clicked */
    on(buttonId, modalId) {
        let element = $id(buttonId);
        if (element) {
            element.setAttribute("target-modal-id", modalId);
            ModalManager.modalInstances[modalId].openCallback = this.openModalCallback.bind(this);
            $on(element, "click", ModalManager.modalInstances[modalId].openCallback);
        }
        else
            console.warn("ModalManager: on: Element with id %s not found", buttonId);
    }

    /* This NEEDS to be called by a configs.js of a view to remove the event listener from the button */
    off(buttonId, modalId) {
        let element = $id(buttonId);
        if (element) {
            element.removeAttribute("target-modal-id");
            if (ModalManager.modalInstances[modalId] && ModalManager.modalInstances[modalId].openCallback) {
                $off(element, "click", ModalManager.modalInstances[modalId].openCallback);
                ModalManager.modalInstances[modalId].openCallback = null;
            }
        }
        else
            console.warn("ModalManager: off: Element with id %s not found", buttonId);
    }

    /*
    Some modals shouldnt open. e.g.: CreateConversation if a covnersation already exists
    To deal with it those modal configs.js files have a hook: async allowedToOpen()
    So we first get the okay to open and then open!
    */
    async tryToShowModal(modalId) {
        const modalHooks = await ModalManager.loadModalHooks(modalId);
        if (!modalHooks) return; // Error msg will be already displayed in the loadModalHooks function
        if (modalHooks.hooks.allowedToOpen) {
            if (await modalHooks.hooks.allowedToOpen.bind(objectToBind(modalHooks))())
                ModalManager.modalInstances[modalId].instance.show();
            else
                console.log("ModalManager: tryToShowModal: Not allowed to open modal (Probably the client got redirected)");
        }
    }
}

// Create and export a single instance
const modalManager = ModalManager.getInstance();
export { modalManager };