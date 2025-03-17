import Cropper from '../../libraries/cropperjs/cropper.esm.js'
import $callToast from '../../abstracts/callToast.js';
import $store from '../../store/store.js';
import router from '../../navigation/router.js';

export default {
    attributes: {
        cropper: undefined,
    },

    methods: {

        openFileExplorer() {
            let element = this.domManip.$id("modal-avatar-cropper-file-input");
            element.click();
        },

        extractImageFile(event) {

            const file = event.target.files[0]; // Get the selected file
            if (!file || !["image/png", "image/jpeg"].includes(file.type)) {
                $callToast("error", "Invalid file type. Please select a PNG or JPEG file.");
                // TODO: close modal or maybe not
                return;
            }
            if (file) {
                const reader = new FileReader(); // Create a FileReader to read the file

                reader.onload = e => {
                    let uploadedImage = this.domManip.$id("modal-avatar-cropper-image-to-crop");
                    uploadedImage.src = e.target.result; // Set the src to the image data
                    // uploadedImage.style.display = 'block'; // Make the img tag visible

                    // Initialize Cropper after the image has fully loaded
                    uploadedImage.onload = () => {
                        // Destroy any previous Cropper instance before creating a new one
                        if (this.cropper) {
                            this.cropper.destroy();
                        }

                        this.cropper = new Cropper(uploadedImage, {
                            aspectRatio: 0.894,
                            background: false,
                            viewMode: 1,
                        });
                    };
                };
                reader.readAsDataURL(file); // Read the file as a data URL
            }
        },

        callFormData(blob) {
            const formData = new FormData();
            formData.append('avatar', blob, 'avatar.png');

            fetch(window.origin + '/api/user/update-avatar/', {
                method: 'PUT',
                body: formData,
                credentials: 'include',
            }).then(response => {
                if (!response.ok) {
                    console.log('Error uploading the image');
                    $callToast("error", "Error on uploading the image.")
                }
                return response.json();
            }).then(data => {
                $store.commit("setUser", { ...$store.fromState("user"), avatar: data.avatar_url.avatar_url });
                this.domManip.$id('profile-nav-avatar').src = `${window.location.origin}/media/avatars/${data.avatar_url.avatar_url}`;
                $callToast("success", data.message);
                router('/profile', { id: $store.fromState("user").id});
            });
        },

        /*  Submits the avatar to the backend */
        submitAvatar() {
            // Extract the cropped portion of the selected image
            const croppedCanvas = this.cropper.getCroppedCanvas({
                width: 186,
                height: 208
            });
            // prepare image to send to backend
            croppedCanvas.toBlob(this.callFormData, 'image/png');
        }

    },

    hooks: {
        beforeOpen () {

            this.openFileExplorer();

            this.domManip.$on(this.domManip.$id("modal-avatar-cropper-file-input"), "change", this.extractImageFile);
            this.domManip.$on(this.domManip.$id("modal-avatar-cropper-btn-open-file-explorer"), "click", this.openFileExplorer);
            this.domManip.$on(this.domManip.$id("modal-avatar-cropper-btn-crop"), "click", this.submitAvatar);
        },

        afterClose () {
            this.domManip.$off(this.domManip.$id("modal-avatar-cropper-file-input"), "change", this.extractImageFile);
            this.domManip.$off(this.domManip.$id("modal-avatar-cropper-btn-open-file-explorer"), "click", this.openFileExplorer);
            this.domManip.$off(this.domManip.$id("modal-avatar-cropper-btn-crop"), "click", this.submitAvatar);
        }
    }
}