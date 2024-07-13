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

        beforeDomInsersion() {
            console.log('beforeDomInsersion', this, window, document);
        },

        afterDomInsersion() {
            console.log('afterDomInsersion', this, window, document);
        },
    }
}