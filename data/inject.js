'use strict';

// https://davidwalsh.name/javascript-download
function downloadFile(data, fileName, type = "text/plain") {
    // Create an invisible A element
    const a = document.createElement("a");
    a.style.display = "none";
    document.body.appendChild(a);

    // Set the HREF to a Blob representation of the data to be downloaded
    a.href = window.URL.createObjectURL(
        new Blob([data], {
            type
        })
    );

    // Use download attribute to set set desired file name
    a.setAttribute("download", fileName);

    // Trigger the download by simulating click
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(a.href);
    document.body.removeChild(a);
}

// Extreme hack to detect when loading is finished.
// window.onload and document.body.onload are unreliable, even with setTimeout.
// This may break suddenly if console log messages change!
// https://stackoverflow.com/a/6455713
(function () {
    var _log = console.log;

    console.log = function (txt) {
        if (txt == "Top bar change") {
            const saveData = localStorage.getItem("__KEY_PLACEHOLDER__");
            downloadFile(saveData, "idleonsave.txt");
        }

        _log.apply(console, arguments);
    }
})();