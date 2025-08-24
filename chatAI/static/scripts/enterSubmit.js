// static/scripts/enterSubmit.js

console.log("contextDelete.js loaded");

(function () {
  function submitForm() {
    const form = document.getElementById("input-form");
    if (!form) return;
    if (typeof form.requestSubmit === "function") form.requestSubmit();
    else form.submit();
  }

  // Element-level handler — wins over most other scripts
  window.__promptKeydown = function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitForm();
      return false; // stop default newline
    }
    // Shift+Enter: let the browser insert a newline naturally
    return true;
  };

  // Also attach a standard listener for redundancy
  document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("prompt");
    if (!input) return;
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitForm();
      }
    }, true);
  });
})();
