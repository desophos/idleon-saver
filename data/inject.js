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

// Wait until first localStorage access so that we know it's available.
var saved = false;
window.addEventListener('storage', () => {
    if (!saved) {
        const saveData = localStorage.getItem("__KEY_PLACEHOLDER__");
        downloadFile(saveData, "idleonsave.txt");
        saved = true;
    }
});