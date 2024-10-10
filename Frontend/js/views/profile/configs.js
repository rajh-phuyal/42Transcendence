import call from '../../abstracts/call.js'
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

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            console.log("yoo");
            console.log(this.routeParams.id);
            console.log(`/user/profile/${this.routeParams.id}`);
            call(`/user/profile/${this.routeParams.id}`, 'GET').then((res)=>{
                console.log(res);
            })            
        },
    }
}