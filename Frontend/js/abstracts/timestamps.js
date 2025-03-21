

function loadTimestamp(timestamp, format = "YYYY-MM-DD HH:mm:ss") {


    if (!timestamp) return "";
    if (!format) return moment.utc(timestamp).local();
    return moment.utc(timestamp).local().format(format);
}

export { loadTimestamp };
