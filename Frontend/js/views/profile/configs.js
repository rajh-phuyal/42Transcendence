export default {
    attributes: {

    },

    methods: {

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {

        },

        beforeDomInsersion() {
            this.$store.commit('setUser', { id: 1, username: 'test' });
            console.log('store', this.$store);
        },

        afterDomInsersion() {

        },
    }
}