(function () {
    function applyMobileStylesheet() {
        const screenHeight = window.innerHeight;
        const screenWidth = window.innerWidth;

        if ((screenWidth <= 900 || screenHeight <= 900) && !document.getElementById('mobile-css')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/mobile.css';
            link.id = 'mobile-css';
            document.head.appendChild(link);
        }
    }

    // Run on initial load
    applyMobileStylesheet();

    // Run again on resize
    window.addEventListener("resize", applyMobileStylesheet);
})();