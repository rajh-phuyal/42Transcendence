export default {
    attributes: {
    },

    methods: {
    },

    hooks: {
        beforeOpen () {
            console.warn("template: beforeOpen");
            return true;
        },
        afterClose () {
            console.warn("template: afterClose");
        }
    }
}