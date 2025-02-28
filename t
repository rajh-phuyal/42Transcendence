[1mdiff --git a/Frontend/js/modals/newConversation/configs.js b/Frontend/js/modals/newConversation/configs.js[m
[1mindex 5bd3b62..1b6b96f 100644[m
[1m--- a/Frontend/js/modals/newConversation/configs.js[m
[1m+++ b/Frontend/js/modals/newConversation/configs.js[m
[36m@@ -47,16 +47,14 @@[m [mexport default {[m
 [m
     hooks: {[m
         beforeOpen () {[m
[31m-            // This function prepares the modal[m
[31m-            // On sucess returns true, on failure returns false[m
[31m-            // Will be called by the ModalManager[m
[32m+[m[32m            /* This function prepares the modal[m
[32m+[m[32m                On sucess returns true, on failure returns false[m
[32m+[m[32m                Will be called by the ModalManager[m
[32m+[m[32m            */[m
 [m
[31m-            console.log("Running beforeOpen hook for modal-new-conversation");[m
             // Fetching the attributes from view and store them locally[m
[31m-[m
[31m-[m
[31m-            // Try to store userId as Number[m
             try {[m
[32m+[m[32m                // Try to store userId as Number[m
                 this.userId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));[m
             } catch {[m
                 console.error("newConversationModal: Couldn't find the userId attribute in the view");[m
[36m@@ -74,8 +72,6 @@[m [mexport default {[m
                 return false;[m
             }[m
 [m
[31m-[m
[31m-[m
             // Set modal title[m
             this.domManip.$id("modal-new-conversation-title").innerText = `Create new conversation with ${this.username}`;[m
             this.domManip.$id("modal-new-conversation-title").setAttribute("data-user-id", this.userId);[m
[1mdiff --git a/Frontend/js/navigation/routes.js b/Frontend/js/navigation/routes.js[m
[1mindex 19db85f..6068535 100644[m
[1m--- a/Frontend/js/navigation/routes.js[m
[1m+++ b/Frontend/js/navigation/routes.js[m
[36m@@ -29,7 +29,8 @@[m [mconst routes = [[m
     {[m
         path: "/chat",[m
         view: "chat",[m
[31m-        requireAuth: true[m
[32m+[m[32m        requireAuth: true.value,[m
[32m+[m[32m        modals: ["createGame"][m
     },[m
     {[m
         path: "/auth",[m
