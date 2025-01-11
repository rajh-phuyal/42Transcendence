import { $id, $on, $off } from '../../abstracts/dollars.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'

export default {
    attributes: {

        tournament: {
            type: "public",
            map: "random",
            userIds: [],
        },

        users: [
            {id: 7, avatar: '../../../assets/avatars/dd6e8101-fde8-469a-97dc-6b8bb9e8296e.png', username: "rajh"},
            {id: 3, avatar: "../../../assets/avatars/73d3a3c0-f3ef-43a1-bdce-d798cb286f27.png", username: "alex"},
            {id: 2, avatar: "../../../assets/avatars/4d39f530-68c8-42eb-ad28-45445424da5b.png", username: "ale"},
            {id: 5, avatar: '../../../assets/avatars/1e3751c5-5e47-45f2-9967-111fd26a6be8.png', username: "anatolii"},
            {id: 10, avatar: "../../../assets/avatars/fe468ade-12ed-4045-80a7-7d3e45be997e.png", username: "xico"},
        ]
    },

    methods: {

        createTournament() {
            const tournamentName = this.domManip.$id("tournament-modal-create-form-name-container-input").value;
            const powerups = this.domManip.$id("tournament-modal-create-form-name-container-checkbox").checked;
            console.log("name:", tournamentName);
            console.log("powerups:",powerups);
            console.log("map:", this.tournament.map);
            console.log("type:", this.tournament.type);
            console.log("ids:", this.tournament.userIds);
        },

        selectMap(chosenMap) {
            const maps = this.domManip.$class("tournament-modal-create-maps-button");
            this.tournament.map = chosenMap.srcElement.name
            for (let element of maps){
                if (element.name != this.tournament.map)
                    element.style.opacity = 0.7;
                else
                    element.style.opacity = 1;
            }
        },



        selectTournamentType(chosenType) {
            const type = this.domManip.$class("tournament-modal-create-form-type-buttons");
            this.tournament.type = chosenType.srcElement.getAttribute("type");
            // TODO: HACHATHON: desable the search bar (disabled attribute) and delet all user cards selected
            console.log("type", this.tournament.type);
            if (this.tournament.type != "public")
                this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").style.display = "flex";
            else
                this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").style.display = "none";

            for (let element of type){
                if (element.getAttribute("type") != this.tournament.type)
                    element.setAttribute('highlight', 'false');
                else
                element.setAttribute('highlight', 'true');
                ;
            }
        },

        deleteInviteUserCard(event) {

            const userId = event.target.parentNode.getAttribute("userId"); 
            console.log("before:", this.tournament.userIds);
            this.tournament.userIds = this.tournament.userIds.filter((element) => element != userId);
            console.log("after:", this.tournament.userIds);
            event.target.parentNode.remove();
            
        },

        createInviteUserCard(userObject) {

            console.log(userObject);
            if (this.tournament.userIds.find(id => id === userObject.id))
                return;
            this.tournament.userIds.push(userObject.id);            

            let template = $id("template-tournament-modal-create-form-invited-user-card").content.cloneNode(true);
    

            const container = template.querySelector(".tournament-modal-create-form-invited-user-card");
            container.setAttribute("userId", userObject.id);
            template.querySelector(".tournament-modal-create-form-invited-user-card-avatar").src = userObject.avatar;
            template.querySelector(".tournament-modal-create-form-invited-user-card-username").textContent = userObject.username;
            this.domManip.$on(template.querySelector(".tournament-modal-create-form-invited-user-card-delete-user"), "click", this.deleteInviteUserCard);
            this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").appendChild(container);
            
        }

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            $off(document, "click", mouseClick);
            $off(document, "mousemove", isHovering);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            this.domManip.$off(element, "click", this.createTournament);
            element = this.domManip.$class("tournament-modal-create-maps-button");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            element = this.domManip.$class("tournament-modal-create-form-type-buttons");
            for (let individualElement of element)
                this.domManip.$on(individualElement, "click", this.selectMap);
        },

        beforeDomInsertion() {
            
        },

        afterDomInsertion() {
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = $id("home-canvas");
            let canvas = canvasData.canvas;

            canvasData.context = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            // Adjust the pixel ratio so it draws the images with higher resolution
            const scale = window.devicePixelRatio;

            canvasData.context.imageSmoothingEnabled = true;
            canvasData.context.scale(scale, scale);

            // build thexport e first frame
            buildCanvas();

            for (let element of this.users)
                this.createInviteUserCard(element);

            $on(document, "click", mouseClick);
            $on(document, "mousemove", isHovering);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            this.domManip.$on(element, "click", this.createTournament);
            element = this.domManip.$class("tournament-modal-create-maps-button");
            for (let individualElement of element)
                this.domManip.$on(individualElement, "click", this.selectMap);
            element = this.domManip.$class("tournament-modal-create-form-type-buttons");
            for (let individualElement of element)
                this.domManip.$on(individualElement, "click", this.selectTournamentType);
        },
    }
}