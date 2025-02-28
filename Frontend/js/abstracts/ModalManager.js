import { $id, $on, $off, $class } from './dollars.js';
import { objectToBind } from '../navigation/router.js';

export default class ModalManager {
    static instance = null;

    static getInstance() {
        if (!ModalManager.instance) {
            ModalManager.instance = new ModalManager();
        }
        return ModalManager.instance;
    }

    static idToFolderName(modalName) {
        const modalFolders = [
            // TODO: Add all modals here
            ["modal-new-conversation", "newConversation"],
            ["modal-template", "template"],
        ];

        const result = modalFolders.find(([modal, _]) => modal === modalName);
        return result ? result[1] : null; // Return filename or null if not found
    }

    static async startBeforeOpenHook(modalId) {
        console.log("Starting beforeOpen hook for modal: ", modalId);
        if (!modalId){
            console.warn("ModalManager: startBeforeOpenHook: modalId is not defined");
            return;
        }

        const folderName = ModalManager.idToFolderName(modalId)
        if (!folderName) {
            console.warn(`ModalManager: startBeforeOpenHook: Couldn't find folder name for modal: ${modalId}`);
            return;
        }

        // Load modal view hooks
        const path = `../modals/${folderName}/configs.js`;
        return await import(path)
            .then(conf => conf.default)
            .then(viewHooks => {
                // Run the function if it exists
                if (viewHooks.hooks && viewHooks.hooks.beforeOpen) {
                    const boundFunction = viewHooks.hooks.beforeOpen.bind(objectToBind(viewHooks));
                    return boundFunction();
                } else {
                    console.warn(`Couldn't find the 'beforeOpen' function for modal: ${modalId}`);
                    return;
                }
        }).catch(err => {
            console.warn(`Couldn't find the 'hooks' function for modal: ${modalId} at path: ${path}`);
            return;
        });
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

    openModal(modalId) {
        let modalElement = $id(modalId);
        if (!modalElement) {
            console.warn("ModalManager: openModal: Element with id %s not found", modalId);
            return
        }
        const modal = new bootstrap.Modal(modalElement);
        if (!modal) {
            console.warn("ModalManager: openModal: Modal with id %s not found", modalId);
            return
        }
        // This function is async and needs to go in arrow function
        (async () => {
            if (await ModalManager.startBeforeOpenHook(modalId))
                modal.show();
        })();
    }

    closeModal(modalId) {
        let modalElement = $id(modalId);
        if(!modalElement) {
            console.warn("ModalManager: closeModal: Element with id %s not found", modalId);
            return
        }
        if (!modalElement) {
            console.warn("ModalManager: closeModal: Modal with id %s not found", modalId);
            return
        }

        const modal = bootstrap.Modal.getInstance(modalElement);
        if (!modal) {
            console.warn("ModalManager: closeModal: Modal instance with id %s not found", modalId);
            return
        }
        modal.hide();
    }
}

// Create and export a single instance
const modalManager = ModalManager.getInstance();
export { modalManager };