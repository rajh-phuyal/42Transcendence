export default class HistoryManager {
    static instance = null;

    constructor() {
        if (HistoryManager.instance) {
            return HistoryManager.instance;
        }
        this.lastPath = null;
        this.lastParams = null;
        HistoryManager.instance = this;
    }

    static getInstance() {
        if (!HistoryManager.instance)
            HistoryManager.instance = new HistoryManager();
        return HistoryManager.instance;
    }

    updateHistory(path, params) {
        console.warn(path, params);
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
        let pathForHistory = "";
        let paramForHistory = JSON.stringify(params);
        let title = "";
        if (path === "/" || path === "/home") {
            title = "Home";
            pathForHistory = "/home";
            paramForHistory = "";
        } else if (path === "/game") {
            title = "Game";
            pathForHistory = path;
        } else if (path === "/tournament") {
            title = "Tournament";
            pathForHistory = path;
        } else if (path === "/profile") {
            title = "Profile";
            pathForHistory = path;
        } else if (path === "/chat") {
            title = "Chat";
            pathForHistory = "/chat";
            paramForHistory = "";
        } else {
            console.log("HistoryManager.updateHistory: Path: '%s' should not be pushed to history", path);
            return;
        }
        // 2. Compare the path with the last page
        // 3. If the paths differ, push the new path to the history
        if (pathForHistory !== this.lastPath || paramForHistory !== this.lastParams) {
            console.warn("HistoryManager.updateHistory: '%s', '%s'", pathForHistory, paramForHistory);
            this.lastPath = path;
            this.lastParams = paramForHistory;
            window.history.pushState(
                {   path:   pathForHistory,
                    params: paramForHistory,
                },
                title,
                pathForHistory
            );
        } else
            console.log("HistoryManager.updateHistory: Paths are the same");
    }
}

// Create and export a single instance
const historyManager = HistoryManager.getInstance();
export { historyManager };
