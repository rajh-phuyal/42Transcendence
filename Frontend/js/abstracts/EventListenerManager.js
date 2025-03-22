import { $id, $on, $off } from './dollars.js';

export class EventListenerManager {
    static #activeListeners = {};
    constructor () {
        if (this instanceof EventListenerManager)
            return null;
    }

    /**
     * @param {String} elementId - The html element ID which will receive the event listener.
     * @param {String} view - View of the event, this refers to which view
     * the element it's associated, so when the view leaves the Router and all it's associated elements
     * event listeners are also removed.
     * @param {String} eventType - Type of event ('click', 'keypress', 'etc')
     * @param {Function} callback - A function to be executed when the event is triggered, it will be deep copied.
     */
    static linkEventListener(elementId, view, eventType, callback) {
        // Check if Element already exists in Event Listener line 2!!!
        if (!EventListenerManager.#activeListeners[elementId]) {
            EventListenerManager.#activeListeners[elementId] = {
                view,
                events: [],
            }
        } else
            EventListenerManager.unlinkEventListener(elementId, eventType);
        EventListenerManager.#addElementEventType(elementId, eventType, callback);
    }

    /**
     * @param {String} elementId - The html element ID which will receive the event listener.
     * @param {String} eventType - Type of event ('click', 'keypress', 'etc')
     */
    static unlinkEventListener(elementId, eventType) {
        // Check if the element is part of the listener, if yes remove the event.
        if (!EventListenerManager.#activeListeners[elementId])
            return ;
        const eventEntry = EventListenerManager.#activeListeners[elementId].events.find((e) => e.eventType === eventType);
        if (!eventEntry)
            return ;
        const element = $id(elementId);
        if (!element)
            return ;
        $off(element, eventEntry.eventType, eventEntry.callback);
        EventListenerManager.#activeListeners[elementId].events = EventListenerManager.#activeListeners[elementId].events.filter((e) => e.eventType != eventType);
    }

    /**
     * @param {String} view - View of the event, this refers to which view
     * the element it's associated, so when the view leaves the Router and all it's associated elements
     * event listeners are also removed.
     */
    static unlinkEventListenersView(view) {
        for (const elementId in EventListenerManager.#activeListeners) {
            if (EventListenerManager.#activeListeners[elementId].view === view) {
                EventListenerManager.#activeListeners[elementId].events.forEach((event) => {
                    EventListenerManager.unlinkEventListener(elementId, event.eventType);
                });
                delete EventListenerManager.#activeListeners[elementId];
            }
        }
    }

    /**
     * @param {String} elementId - The html element ID which will receive the event listener.
     * @param {String} eventType - Type of event ('click', 'keypress', 'etc')
     */
    static #addElementEventType(elementId, eventType, callback) {
        const newEventElement = {
            eventType,
            callback: callback?.bind(callback)
        };
        const element = $id(elementId);
        if (!element)
            return ;
        $on(element, newEventElement.eventType, newEventElement.callback);
        EventListenerManager.#activeListeners[elementId].events.push(newEventElement);
    }
};