import { anotherFunction } from './helpers.js';

export default {
    variables: {
        someVar: 'someValue',
    },

    methods: {
        doSomething() {
            console.log('doSomething: ', anotherFunction());
            console.log('doSomething', this, window, document);
            this.methods.doSomethingElse();
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
            console.log('this.vars.someVar', this.variables.someVar);
            this.methods.doSomething();
        },

        beforeDomInsersion() {
            console.log('beforeDomInsersion', this);
            this.variables.someVar = 'someOtherValue';
        },

        afterDomInsersion() {
            console.log('afterDomInsersion', this);
            console.log('this.vars.someVar', this.variables.someVar);
        },
    }
}