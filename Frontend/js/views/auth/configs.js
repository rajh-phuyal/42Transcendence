import { anotherFunction } from './helpers.js';

export default {
    attributes: {
        someVar: 'someValue',
    },

    methods: {
        doSomething() {
            console.log('doSomething: ', anotherFunction());
            console.log('doSomething', this, window, document);
            this.doSomethingElse();
        },

        doSomethingElse() {
            console.log('doSomethingElse', this, window, document);
        }
    },

    hooks: {
        beforeRouteEnter() {
            console.log('beforeRouteEnter', this);
        },

        beforeRouteLeave() {
            console.log('beforeRouteLeave', this);
            console.log('this.vars.someVar', this.someVar);
            this.doSomething();
        },

        beforeDomInsersion() {
            console.log('beforeDomInsersion', this);
            this.someVar = 'someOtherValue';
        },

        afterDomInsersion() {
            console.log('afterDomInsersion', this);
            console.log('this.vars.someVar', this.someVar);
        },
    }
}