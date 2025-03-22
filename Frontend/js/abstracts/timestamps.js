
function loadTimestamp(timestamp, format = "YYYY-MM-DD HH:mm:ss") {
    if (!timestamp) return "";

    const momentObj = moment.utc(timestamp);
    if (!momentObj.isValid()) {
        return timestamp;
    }

    return format ? momentObj.local().format(format) : momentObj.local();
}

export { loadTimestamp };
