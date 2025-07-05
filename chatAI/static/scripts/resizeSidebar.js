document.addEventListener('DOMContentLoaded', () => {
    console.log("resizeSidebar.js loaded");

    function initResize(e) {
        console.log("Resize started");
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResize);
    }

    function resize(e) {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;
        let newWidth = e.clientX;
        const min = 100;
        const max = window.innerWidth * 0.5;
        sidebar.style.width = Math.min(max, Math.max(min, newWidth)) + 'px';
    }

    function stopResize() {
        console.log("Resize stopped");
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
    }

    function bindResizer() {
        const sidebar = document.getElementById('sidebar');
        const resizer = document.getElementById('resizer');

        if (sidebar && resizer && !resizer.dataset.bound) {
            console.log("Sidebar and resizer found. Binding resize logic.");
            resizer.dataset.bound = "true";
            resizer.addEventListener('mousedown', initResize);
            resizer.addEventListener('mousedown', () => {
                console.log("mousedown fired on resizer");
            });
        }
    }

    // Try binding immediately
    bindResizer();

    // Watch for dynamic DOM changes
    const observer = new MutationObserver(bindResizer);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // ✅ Clear the response box on New Conversation click
    const newConversationButton = document.getElementById('new-conversation');
    const responseBox = document.getElementById('response-box');

    if (newConversationButton && responseBox) {
        newConversationButton.addEventListener('click', () => {
            responseBox.innerHTML = '';
            console.log("Cleared response-box for new conversation.");
        });
    }
});
