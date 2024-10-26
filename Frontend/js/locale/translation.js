// translations
import $store from '../store/store.js';

/**
 *
 * @param {String} namespace - namespace of the translation
 * @param {String} key - key of the translation
 * @param {Object} param - param to replace in the translation
 * @returns {String} string mapped to the key and replaced with the param
 */
export const $translate = (namespace, key, param = null) => {
    const locale = $store.state.locale;
    const translation = $store.state.translations[namespace][key][locale];

    if (!translation) return key;

    if (!param) return translation;

    return translation.replace(/{{\s*(\w+)\s*}}/g, (match, paramKey) => {
        return param[paramKey];
    });
};