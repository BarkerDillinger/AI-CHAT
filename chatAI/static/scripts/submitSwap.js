// /static/scripts/submitSwap.js
(() => {
  const form = document.getElementById("input-form");
  const btn  = document.getElementById("submit-button");
  const img  = document.getElementById("submit-img");
  if (!form || !btn || !img) return;

  const DEFAULT_SRC = btn.dataset.srcDefault || img.getAttribute("src");
  const A_SRC = btn.dataset.srcA || "/static/images/thinking1.png";
  const B_SRC = btn.dataset.srcB || "/static/images/thinking2.png";

  let flashing = false;
  let intervalId = null;
  let timeoutId = null;

  function startFlash() {
    if (flashing) return;
    flashing = true;

    // alternate images every 100ms
    let state = false;
    img.src = A_SRC;
    intervalId = setInterval(() => {
      state = !state;
      img.src = state ? A_SRC : B_SRC;
    }, 100);

    // stop after 2 seconds
    timeoutId = setTimeout(stopFlash, 2000);

    // IMPORTANT: disable AFTER the native submit has already queued
    // so disabling doesn't cancel submission
    setTimeout(() => { btn.disabled = true; }, 0);
  }

  function stopFlash() {
    if (!flashing) return;
    flashing = false;
    if (intervalId) clearInterval(intervalId);
    if (timeoutId) clearTimeout(timeoutId);
    intervalId = timeoutId = null;
    img.src = DEFAULT_SRC;
    btn.disabled = false;
  }

  // Run for both mouse submit and Enter-key submit
  form.addEventListener("submit", () => {
    startFlash();
    // do NOT preventDefault; allow the form to proceed
  });

  // If user navigates back, ensure we’re reset
  window.addEventListener("pageshow", () => stopFlash());
})();
