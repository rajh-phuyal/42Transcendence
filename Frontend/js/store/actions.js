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

        $store.commit('setTranslations', translations);
    }
}