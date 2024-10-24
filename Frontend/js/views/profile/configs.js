import call from '../../abstracts/call.js'
import { $id, $on } from '../../abstracts/dollars.js';
import { populateInfoAndStats } from './script.js';
import { buttonObjects } from "./objects.js"

export default {
    attributes: {
        buttonTopLeft: undefined,
        buttonTopMiddle: undefined,
        buttonTopRight: undefined,
        buttonBottomLeft: undefined,
        buttonBottomRight: undefined,
        result: undefined,
    },

    methods: {
        populateButtons(){
            if (this.result.relationship.state != "yourself")
            {
                if (this.result.relationship.is_blocking)
                    this.buttonTopLeft
            }
        }

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            console.log("yooo");
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                console.log(res);
                this.result = res;
                populateInfoAndStats(res);
                populateButtons(friendshipObjects[4]);
                if (res.is_blocked)
                    blackout();

                
                
                // callback functions
                let element = $id("button-top-right");
                $on(element, "click", friendshipObjects[4].buttonTopRightMethod);
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/