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
            // call(`/user/profile/${this.routeParams.id}`, 'GET').then((res)=>{
            //     console.log(res);
            // })
            fetch(`/user/profile/${this.routeParams.id}`, {
                method: 'GET', // Explicitly specify the method (optional since GET is default)
            })
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json(); // Parse the response as JSON
              })
              .then(data => {
                console.log(data); // Handle the parsed data
              })
              .catch(error => {
                console.error('Error:', error); // Handle errors
              });
            
        },
    }
}