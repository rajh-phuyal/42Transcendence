import call from '../../abstracts/call.js'
import { $id, $on, $queryAll, $off } from '../../abstracts/dollars.js';
import { populateInfoAndStats } from './script.js';
import { buttonObjects } from "./objects.js"
import router from '../../navigation/router.js';
import Cropper from '../../libraries/cropperjs/cropper.esm.js'

export default {
    attributes: {
        buttonTopLeft: {
            image: undefined,
            method: undefined,
        },
        buttonTopMiddle: {
            image: undefined,
            method: undefined,
        },
        buttonTopRight: {
            image: undefined,
            method: undefined,
        },
        result: undefined,
        frendshipStateIndex: undefined,
        blockerState: false,
        cropper: undefined,

        buttonSettings: {
            friend: {
                path: "../../../../assets/profileView/friendsIcon.png",
                index: 0,
            },
            noFriend: {
                path: "../../../../assets/profileView/firendRequestIcon.png",
                index: 1,
            },
            requestReceived: {
                path: "../../../../assets/profileView/receivedFriendRequest.png",
                index: 2,
            },
            requestSent: {
                path: "../../../../assets/profileView/sentFriendRequest.png",
                index: 3,
            },
            
        }
    },

    methods: {
        insertAvatar() {
            const element = $id("avatar");
            element.src = 'https://localhost/media/avatars/' + this.result.avatarUrl;
        },

        setupTopLeftButton() {
            if (this.result.relationship.state != "yourself")
                {
                    this.buttonTopLeft.method = this.friendshipMethod;
                    this.buttonTopLeft.image = this.buttonSettings[this.result.relationship.state].path;
                    this.frendshipStateIndex = this.buttonSettings[this.result.relationship.state].index;
                    if (this.result.relationship.isBlocking) {
                        this.buttonTopLeft.image = "../../../../assets/profileView/blockedUserIcon.png";
                        this.blockerState = true;
                    }
                }
        },
        setupTopMiddleButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopMiddle.method = this.profileEditMethod;
                this.buttonTopMiddle.image = "../../../../assets/profileView/penIcon.png";
            }
            else {
                if (this.result.newMessage)
                    this.buttonTopMiddle.image = "../../../../assets/profileView/unreadMessageIcon.png";
                else
                    this.buttonTopMiddle.image = "../../../../assets/profileView/sendMessageIcon.png";
                    this.buttonTopMiddle.method = this.messageMethod;
            }
        },
        setupTopRightButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/profileView/logoutIcon.png";
                this.buttonTopRight.method = this.logoutMethod;
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/profileView/invitePongIcon.png";
            }
        },
        putImagesInButtons() {
            let element = $id("button-top-left");
            if (this.buttonTopLeft.image)
                element.src = this.buttonTopLeft.image;
            else
                element.style.display = "none";
            element = $id("button-top-middle");
            element.src = this.buttonTopMiddle.image;
            element = $id("button-top-right");
            if (this.buttonTopRight.image)
                element.src = this.buttonTopRight.image;
            else
                element.style.display = "none";
            element = $id("button-bottom-left");
            element.src = "../../../../assets/profileView/gamingHistoryIcon.png";
            element = $id("button-bottom-right");
            element.src = "../../../../assets/profileView/FriendsListIcon.png";
        },
        
        populateButtons(){
            this.setupTopLeftButton();
            this.setupTopMiddleButton();
            this.setupTopRightButton();
            this.putImagesInButtons();
        },

        blackout() {

            let elements = $queryAll(".blackout, .game-stats-parameters, .progress, .last-seen-image, .button-bottom-left, .button-bottom-right")
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }
        },

        hideElement(elementId){
            let element = $id(elementId)
            element.style.display = "none";
        },
        showElement(elementId){
            let element = $id(elementId)
            element.style.display = "block";
        },

        profileEditMethod() {
            this.hideElement("edit-profile-modal-form");   
            this.hideElement("edit-profile-modal-avatar-change");   
            this.hideElement("edit-profile-modal-password-change");
            this.showElement("edit-profile-modal-autentication");
            

            let modalElement = $id("edit-profile-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        editProfileAuthSubmit() {
            // to show error message
            // let element = $id("edit-profile-modal-autentication-error");
            // element.style.display = "block";

            this.hideElement("edit-profile-modal-autentication");   
            this.showElement("edit-profile-modal-form");
        },

        changePasswordMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-password-change");
        },
        changeAvatarMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-avatar-change");
            this.hideElement("edit-profile-modal-avatar-change-crop-image");
        },

        friendshipMethod() {

            let blockIndex;
            if (this.blockerState)
                blockIndex = 5;
            else
                blockIndex = 4;


            // friendship portion of the modal
            let element = $id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.frendshipStateIndex].text;
            if (this.result.relationship.state == "noFriend" && this.result.relationship.isBlocked)
            {
                element.style.display = "none";
                this.hideElement("friendship-modal-friendship-primary-button");
            }

            if (!buttonObjects[this.frendshipStateIndex].secundaryButton)
                this.hideElement("friendship-modal-friendship-secundary-button");

            // blocking portion of the friendshop modal
            if (this.result.relationship.state == "requestReceived" || this.result.relationship.state == "requestSent")
                this.hideElement("friendship-modal-block");

            else {
                element = $id("friendshp-modal-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }

            let modalElement = $id("friendship-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        openFileExplorer() {
            let element = $id("edit-profile-modal-avatar-change-file-input");
            element.click();
        },
        
        cropImage() {
            
            const croppedCanvas = this.cropper.getCroppedCanvas({
                width: 186,
                height: 208
            });
            
            const croppedImageUrl = croppedCanvas.toDataURL('image/png');
            let croppedImageElement = $id("edit-profile-modal-avatar-change-cropped-image");
            croppedImageElement.src = croppedImageUrl;

            croppedCanvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('avatar', blob, 'avatar.png'); // Append file to FormData
        
                try {
                    console.log(formData);
                    const response = await fetch('user/update-avatar/', {
                        method: 'POST',
                        body: formData
                    });
                
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                
                    const responseData = await response.json();
                    console.log('Upload successful:', responseData);
                } catch (error) {
                    console.error('Upload failed:', error);
                }
                
            }, 'image/png');
            // croppedCanvas.toBlob(async (blob) => {
            //     // Create a FormData object
            //     const formData = new FormData();
            //     formData.append('avatar', blob, 'avatar.png'); // Add file with key 'avatar'
        
            //     // Call API with FormData
            //     try {
            //         const response = await call('user/update-avatar/', 'POST', formData);
            //         console.log('Upload successful:', response);
            //     } catch (error) {
            //         console.error('Upload failed:', error);
            //     }
            // }, 'image/png'); // Specify image type as 'image/png' or 'image/jpeg'


            // console.log(croppedImageUrl);
            // call('user/update-avatar/', 'POST', { avatar: croppedImageUrl});
            // console.log("element:", croppedImageElement);
            // this.showElement(croppedImageElement);


            // let uploadedImage = $id("edit-profile-modal-avatar-change-uploaded-image"); 
            // let imageSrc = uploadedImage.src;
            // let croppedImage = this.cropper.getCroppedCanvas().toDataUrl(imageSrc);
            // uploadedImage.src = croppedImage;
        },

        extractFile(event) {
            const file = event.target.files[0]; // Get the selected file
            if (file) {
                const reader = new FileReader(); // Create a FileReader to read the file

                reader.onload = e => {
                    let uploadedImage = $id("edit-profile-modal-avatar-change-uploaded-image");
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

        messageMethod() {
            router("/chat");
        },
        
        logoutMethod() {
            router("/logout");
        }

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            let element = $id("button-top-left");
            $off(element, "click", this.buttonTopLeft.method);
            element = $id("button-top-middle");
            $off(element, "click", this.buttonTopMiddle.method);
            element = $id("button-top-right");
            $off(element, "click", this.buttonTopRight.method);
            element = $id("edit-profile-modal-autentication-submit-button");
            $off(element, "click", this.editProfileAuthSubmit);
            element = $id("edit-profile-modal-form-change-password-button");
            $off(element, "click", this.changePasswordMethod);
            element = $id("edit-profile-modal-form-change-avatar-button");
            $on(element, "click", this.changeAvatarMethod);

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            console.log(this.routeParams);
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                this.result = res;
                console.log(res);
                this.insertAvatar();
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                {
                    console.log("is blocked");
                    this.blackout();
                }

                
                
                // callback functions
                if (this.buttonTopLeft.method) {
                    let element = $id("button-top-left");
                    $on(element, "click", this.buttonTopLeft.method);
                }
                if (this.buttonTopMiddle.method) {
                    let element = $id("button-top-middle");
                    $on(element, "click", this.buttonTopMiddle.method);
                }
                if (this.buttonTopRight.method) {
                    let element = $id("button-top-right");
                    $on(element, "click", this.buttonTopRight.method);
                }

                let element = $id("edit-profile-modal-autentication-submit-button");
                $on(element, "click", this.editProfileAuthSubmit);
                element = $id("edit-profile-modal-form-change-password-button");
                $on(element, "click", this.changePasswordMethod);
                element = $id("edit-profile-modal-form-change-avatar-button");
                $on(element, "click", this.changeAvatarMethod);
                element = $id("edit-profile-modal-avatar-change-upload-button");
                $on(element, "click", this.openFileExplorer);
                element = $id("edit-profile-modal-avatar-change-file-input");
                $on(element, "change", this.extractFile);
                element = $id("edit-profile-modal-avatar-change-crop-image");
                $on(element, "click", this.cropImage);
                
            })
            // on error?
        },
    }
}
