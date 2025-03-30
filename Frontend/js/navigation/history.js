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

    updateHistory(path, paramsString) {
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
        if (path === "/" || path === "/home") {
            pathForHistory = "/home";
            paramsString = "";
        } else if (path === "/game") {
            pathForHistory = path;
        } else if (path === "/tournament") {
            pathForHistory = path;
        } else if (path === "/profile") {
            pathForHistory = path;
        } else if (path === "/chat") {
            pathForHistory = "/chat";
            paramsString = "";
        } else {
            console.log("HistoryManager: Path: '%s' should not be pushed to history", path);
            return;
        }
        // 2. Compare the path with the last page
        // 3. If the paths differ, push the new path to the history
        if (pathForHistory !== this.lastPath || paramsString !== this.lastParams) {
            this.lastPath = pathForHistory;
            this.lastParams = paramsString;
            const fullUrl = paramsString ? pathForHistory + paramsString : pathForHistory;

            console.log("HistoryManager: pushingState: '%s', '%s' as '%s'", pathForHistory, paramsString, fullUrl);
            window.history.pushState(
                {   path:   pathForHistory,
                    params: paramsString,
                },
                "",
                fullUrl
            );
        } else
            console.log("HistoryManager: path is the same as the last one, not pushing to history");
    }

    /* Converts a string of parameters to an object
        "?id=1&name=John"0 => { id: 1, name: "John" }
    */
    argsStringToObject(argsString) {
        let paramsObject = {};
        if (argsString) {
            // First remove the question at index 1 if it exists
            if (argsString[0] === '?')
                argsString = argsString.slice(1);
            paramsObject = argsString
                .split('&')                 // Split by '&' if there are multiple parameters (but I guess we don't have this)
                .reduce((acc, param) => {
                  const [key, value] = param.split('=');    // Split each key-value pair
                  acc[key] = decodeURIComponent(value);     // Assign the key-value pair to the accumulator
                  return acc;
                }, {});
        }
        return paramsObject;
    }
}

// Create and export a single instance
const historyManager = HistoryManager.getInstance();
export { historyManager };
