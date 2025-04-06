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
    // Trying to get clients local language e.g. en-US
    const locale = $store.fromState('locale');
    if(!locale) {
        console.warn("No locale set in store");
        return key;
    }

    // Trying to load the translation dict from store
    let translation = $store.fromState('translations')?.[namespace]?.[key]?.[locale];
    if (!translation) {
        console.log(`Translation for ${namespace}.${key} not found for locale ${locale}`);
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

async function loadAndExecuteTranslations(subject, modal=false) {
    try {
        let filePath = "";
        if (modal)
            filePath = `../js/modals/${subject}/staticTranslations.json`;

        else
            filePath = `../js/views/${subject}/staticTranslations.json`;
        const translationMap = await fetch(filePath);

        if (translationMap.ok) {
            const translationMapData = await translationMap.json();
            for (const key in translationMapData) {
                let targetElement = $id(key)
                if(!targetElement) {
                    console.log("Error in staticTranslation.js for view: %s; html element '%s' not found", subject, key);
                    continue;
                }
                let translatedString = translate(subject, translationMapData[key]);
                // console.log("Static element translated: %s; translation: %s", key, translatedString);
                targetElement.innerHTML = translatedString;
            }
        }
    } catch(error) {
        console.log("Error on translation: Check if file: 'staticTranslations.json' exists for this subject: %s; error: %s", subject, error);
    }
}

export async function staticTranslator(viewName) {
    const routeObject = routes.find(route => route.view === viewName);
    await loadAndExecuteTranslations(viewName);
    if (!routeObject.modals)
        return ;
    for (let modal of routeObject.modals)
        await loadAndExecuteTranslations(modal, true);
};