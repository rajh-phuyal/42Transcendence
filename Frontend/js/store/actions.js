import { routes } from "../navigation/routes.js";

export const actions = {
    loadTranslations: async ($store) => {
        let translations = {};

        for (const view of routes.map(route => route.view)) {
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
            }
        }

        $store.commit('setTranslations', translations);
    }
}