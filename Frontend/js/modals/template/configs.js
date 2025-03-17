export default {
    attributes: {
    },

    methods: {
    },

    hooks: {
        async allowedToOpen() {
            return false;
        },

        beforeOpen () {
            console.warn("template: beforeOpen");
            return true;
        },
        afterClose () {
            console.warn("template: afterClose");
        }
    }
}