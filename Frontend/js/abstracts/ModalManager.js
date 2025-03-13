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
    ["modal-template-image", "templateImage"],
];
export default class ModalManager {
    static instance = null;
    static modalInstances = {}; // Here we store all modal instances. To make sure we instantiate each modal only once

    /* For the singleton export */
    static getInstance() {
        if (!ModalManager.instance) {
            ModalManager.instance = new ModalManager();
        }
        return ModalManager.instance;
    }

    static idToFolderNameStatic(modalName) {
        const result = modalFolders.find(([modal, _]) => modal === modalName);
        return result ? result[1] : null; // Return filename or null if not found
    }

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

        // Only continue if the modal was not already set up
        if (ModalManager.modalInstances[modalId]) return;

        // Create a new instance of the modal
        ModalManager.modalInstances[modalId] = new bootstrap.Modal(modalElement);

        const modalHooks = await ModalManager.loadModalHooks(modalId);
        if (!modalHooks) return; // Error msg will be already displayed in the loadModalHooks function

        const modalConfig = objectToBind(modalHooks);

        // Prevent duplicate event listeners by removing them first
        $off(modalElement, 'show.bs.modal');
        $off(modalElement, 'hidden.bs.modal');
        // Attach Bootstrap event listeners
        $on(modalElement, 'show.bs.modal', async () => {
            console.log(`ModalManager: Opening modal: ${modalId}`);
            if (modalHooks.hooks.beforeOpen) {
                const shouldOpen = await modalHooks.hooks.beforeOpen.bind(modalConfig)();
                if (!shouldOpen) {
                    console.warn(`ModalManager: beforeOpen returned false. Preventing modal ${modalId} from opening.`);
                    ModalManager.modalInstances[modalId].hide();
                }
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

    async openModal(modalId) {
        let modalElement = $id(modalId);
        if (!modalElement) {
            console.warn(`ModalManager: openModal: Modal element not found: ${modalId}`);
            return;
        }
        await this.setupModal(modalId);
        ModalManager.modalInstances[modalId].show();
    }

    closeModal(modalId) {
        console.warn(`ModalManager: closeModal: Closing modal with id ${modalId}`);
        if (!ModalManager.modalInstances[modalId]) return;
        ModalManager.modalInstances[modalId].hide();
    }

    destroyAllModals() {
        console.log("ModalManager: Destroying all loaded modals");
        Object.keys(ModalManager.modalInstances).forEach(modalId => {
            const modalElement = $id(modalId);
            const modalInstance = ModalManager.modalInstances[modalId];
            if (modalInstance) {
                modalInstance.hide();
                modalInstance.dispose();
            }
            // Remove all Bootstrap event listeners
            if (modalElement) {
                $off(modalElement, 'show.bs.modal');
                $off(modalElement, 'hidden.bs.modal');
            }
        });
        ModalManager.modalInstances = {}; // Reset all instances
    }

    idToFolderName(modalName) {
        const result = modalFolders.find(([modal, _]) => modal === modalName);
        return result ? result[1] : null; // Return filename or null if not found
    }

    folderNameToId(folderName) {
        const result = modalFolders.find(([_, folder]) => folder === folderName);
        return result ? result[0] : null; // Return modal ID or null if not found
    }

    on(buttonId, modalId) {
        let element = $id(buttonId);
        if (element)
            $on(element, "click", () => this.openModal(modalId));
        else
            console.warn("ModalManager: on: Element with id %s not found", buttonId);
    }

    off(buttonId) {
        let element = $id(buttonId);
        if (element)
            $off(element, "click", () => this.openModal(modalId));
        else
            console.warn("ModalManager: off: Element with id %s not found", buttonId);
    }
}

// Create and export a single instance
const modalManager = ModalManager.getInstance();
export { modalManager };