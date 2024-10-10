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
            console.log("sss");
            console.log(this.routeParams.id);
            console.log(`user/profile/${this.routeParams.id}`);
            call("user/profile/1/", "GET").then((res)=>{
                console.log(res);
            })            
        },
    }
}