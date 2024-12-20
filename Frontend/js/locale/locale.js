import $store from '../store/store.js';

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