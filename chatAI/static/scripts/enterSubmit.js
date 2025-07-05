document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("prompt");
    const form = document.getElementById("input-form");

    textarea.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault(); // Prevent newline
            form.submit();      // Submit the form
        }
    });
});
// This script listens for the Enter key press in the textarea with id "prompt".
// If the Enter key is pressed without the Shift key, it prevents the default behavior