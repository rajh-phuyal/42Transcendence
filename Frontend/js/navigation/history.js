export default class HistoryManager {
    static instance = null;

    constructor() {
        if (HistoryManager.instance) {
            return HistoryManager.instance;
        }
        this.lastPage = null;
        HistoryManager.instance = this;
    }

    static getInstance() {
        if (!HistoryManager.instance)
            HistoryManager.instance = new HistoryManager();
        return HistoryManager.instance;
    }

    updateHistory(path, params) {
        console.warn("HistoryManager.updateHistory: ", path);
        console.warn("HistoryManager.updateHistory: ", params);
        // So since we are not using the prams in the bes way, we have the
        // situation that sometimes they are mandatory and sometimes they are not.
        // This is a bad practice and should be fixed.
        // Anyhow to make the history work we do the following:
        //      PATH            PARAMS MANATORY    PUSH TO HISTORY
        // ---------------------------------------------------------------------
        //    "/"                      -          /home
        //    "/home"                  -          /home
        //    "/game"                  x          /game & params
        //    "/tournament"            x          /tournament & params
        //    "/profile"               x          /profile & params
        //    "/chat"                  -          /chat
        //    "/auth"                  -          -
        //    "/404"                   -          -
        //    "/barely-responsive"     -          -

        // 1.Get the right path
        let pathForHistory = path;
        let title = "";
        if (path === "/" || path === "/home") {
            title = "Home";
            pathForHistory = "/home";
        } else if (path === "/game") {
            title = "Game";
            pathForHistory = path + "?" + params;
        } else if (path === "/tournament") {
            title = "Tournament";
            pathForHistory = path + "?" + params;
        } else if (path === "/profile") {
            title = "Profile";
            pathForHistory = path + "?" + params;
        } else if (path === "/chat") {
            title = "Chat";
            pathForHistory = "/chat";
        } else
            return;
        // 2. Compare the path with the last page
        // 3. If the paths differ, push the new path to the history
        console.error("HistoryManager.updateHistory: ", pathForHistory);
        if (path !== this.lastPage) {
            this.lastPage = path;
            window.history.pushState({ path: pathForHistory }, title, pathForHistory);
        }
    }
}

// Create and export a single instance
const historyManager = HistoryManager.getInstance();
export { historyManager };
