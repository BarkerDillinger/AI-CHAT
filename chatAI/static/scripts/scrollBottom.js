function scrollToBottom() {
  const scrollbtm = document.getElementById("response-box");
  if (!scrollbtm) return;

  requestAnimationFrame(() => {
    // Delay slightly to ensure layout is complete
    setTimeout(() => {
      scrollbtm.scrollTop = scrollbtm.scrollHeight;
    }, 0);
  });
}

window.addEventListener("load", scrollToBottom);  // More reliable than DOMContentLoaded
