import $store from '../store/store.js';
import { routes } from '../navigation/routes.js';
import { $id } from '../abstracts/dollars.js'

/**
 *
 * @param {String} namespace - namespace of the translation
 * @param {String} key - key of the translation
 * @param {Object} param - param to replace in the translation
 * @returns {String} string mapped to the key and replaced with the param
 */
export const translate = (namespace, key, params = null) => {
    const locale = $store.state.locale;

    let translation = $store.state.translations?.[namespace]?.[key]?.[locale];

    if (!translation) {
        console.warn(`Translation for ${namespace}.${key} not found for locale ${locale}`);
        return key;
    }

    if (!params) return translation;

    let regex = new RegExp(`(?<!\\\\){([^}]+)}`, 'g');
    let matches = translation.matchAll(regex);
    for (const match of matches) {
        const [matched, key] = match;
        translation = translation.replace(matched, params[key]);
    }

    return translation;
};

async function loadAndExecuteTranslations(subject) {
    try {
        let translationMap = await fetch(`../views/${subject}/staticTranslations.json`);
        if (translationMap.ok) {
            const translationData = await translationMap.json();
            for (const [key, value] of translationData)
                $id(key) = translate(subject, value);
        }
    } catch(error) {
        console.error("Error on translation:", error);
    }
}

export function staticTranslator(viewName) {
    const routeObject = routes.find(route => route.view === viewName);

    loadAndExecuteTranslations(viewName);

    if (!routeObject.modals)
        return ;
    for (modal of routeObject.modals)
        loadAndExecuteTranslations(modal);
};