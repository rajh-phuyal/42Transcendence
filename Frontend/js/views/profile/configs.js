export default {
    attributes: {
        someVar: 'someValue',
    },

    methods: {
        doSomething() {
            console.log('doSomething', this, window, document);
        }
    },

    hooks: {
        beforeRouteEnter() {
            console.log('beforeRouteEnter', this, window, document);
        },

        beforeRouteLeave() {
            console.log('beforeRouteLeave', this, window, document);
        },

        beforeDomInsertion() {
            console.log('beforeDomInsertion', this, window, document);
        },

        afterDomInsertion() {
            console.log('afterDomInsertion', this, window, document);
        },
    }
}