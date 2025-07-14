document.addEventListener("DOMContentLoaded", function () {
    const newButton = document.getElementById("new-conversation");
    if (newButton) {
        newButton.addEventListener("click", function () {
            // Redirect to /new — FastAPI will create a new conversation and redirect us
            window.location.href = "/new";
        });
    }
});
