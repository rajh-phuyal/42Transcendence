//import Cropper from '../../libraries/cropperjs/cropper.esm.js'

// TODO:
        //------------------------------
        // THIS CODE IS GOOD! JUST NEEDS TO BE REVIEWED AND ADJUSTED TO THE NEW MODAL
        //------------------------------
        /*

        changeAvatarMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-avatar-change");
            this.hideElement("edit-profile-modal-avatar-change-crop-image");
            this.domManip.$id("edit-profile-modal").focus();
        },



        openFileExplorer() {
            let element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
            element.click();
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
				$id('profile-nav-avatar').src = `${window.location.origin}/media/avatars/${data.avatar_url.avatar_url}`;
                this.hideModal("edit-profile-modal");
                $callToast("success", data.message);
                router('/profile', { id: $store.fromState("user").id});
            });
        },

        submitAvatar() {

            // Extract the cropped portion of the selected image
            const croppedCanvas = this.cropper.getCroppedCanvas({
                width: 186,
                height: 208
            });

            // prepare image to send to backend
            croppedCanvas.toBlob(this.callFormData, 'image/png');
        },

        extractFile(event) {
            const file = event.target.files[0]; // Get the selected file
            if (!file || !["image/png", "image/jpeg"].includes(file.type)) {
                $callToast("error", "Invalid file type. Please select a PNG or JPEG file.");
                // TODO: close modal
                return;
            }
            if (file) {
                const reader = new FileReader(); // Create a FileReader to read the file

                reader.onload = e => {
                    let uploadedImage = this.domManip.$id("edit-profile-modal-avatar-change-uploaded-image");
                    uploadedImage.src = e.target.result; // Set the src to the image data
                    uploadedImage.style.display = 'block'; // Make the img tag visible

                    // Initialize Cropper after the image has fully loaded
                    uploadedImage.onload = () => {
                        // Destroy any previous Cropper instance before creating a new one
                        if (this.cropper) {
                            this.cropper.destroy();
                        }

                        this.cropper = new Cropper(uploadedImage, {
                            aspectRatio: 0.894, // Adjust aspect ratio as needed
                            viewMode: 1,
                        });
                        this.showElement("edit-profile-modal-avatar-change-crop-image");
                    };
                };

                reader.readAsDataURL(file); // Read the file as a data URL
            }
        },
        */