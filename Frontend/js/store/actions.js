export const actions = {
    loadTranslations: async ($store, views) => {
        let translations = {};

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
            }
        }

        $store.commit('setTranslations', translations);
    }
}