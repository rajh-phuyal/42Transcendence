import { translate } from '../../locale/locale.js';

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
			let text = this.domManip.$id("dont-resize");
			text.innerText = translate("barely-responsive", "title");
        }
    }
}