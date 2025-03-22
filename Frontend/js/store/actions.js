import { routes } from "../navigation/routes.js";

/**
 * @param {Object} $store - the store object
 * @param {Array} views - the views to load the translations for
 */

export const actions = {
    loadTranslations: async ($store, views) => {
        let translations = {};

        try {
            // load the global translations
            const globalTranslations = await fetch(`../js/locale/translations.json`);
            const translationsData = await globalTranslations.json();

            for (const [key, value] of Object.entries(translationsData)) {
                translations[`global:${key}`] = value;
            }

        } catch (error) {
            console.error("Error loading global translations", error);
        }

        // Load translations of the views
        for (const view of views) {
            try {
                const viewTranslation = await fetch(`../js/views/${view}/translations.json`);

                if (!viewTranslation.ok) {
                    translations[view] = {};
                    continue;
                }
                const translationData = await viewTranslation.json();
                translations[view] = translationData;

            } catch (error) {
                translations[view] = {};
                console.error("Error loading view translations", error);
            }
        }

        // Load translations of the modals

        const modals = routes.map(route => route.modals);

        for (let modalsArray of modals) {
            if (!modalsArray)
                continue ;
            for (let modal of modalsArray) {
                try {
                    if (translations[modal])
                        continue ;
                                        const modalTranslation = await fetch(`../js/modals/${modal}/translations.json`);
                    if (!modalTranslation.ok) {
                        translations[modal] = {};
                        continue;
                    }
                    const modalTranslationData = await modalTranslation.json();
                    translations[modal] = modalTranslationData;
                } catch (error) {
                    translations[modal] = {};
                    console.error("Error loading view translations", error);
                }
            }
        }

        $store.commit('setTranslations', translations);
    }
}