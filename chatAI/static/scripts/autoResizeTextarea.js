document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.querySelector('textarea');

    if (!textarea) return;

    const maxHeight = window.innerHeight * 0.3;

    function autoResize() {
        textarea.style.height = 'auto'; // Reset height
        const scrollHeight = Math.min(textarea.scrollHeight, maxHeight);
        textarea.style.height = scrollHeight + 'px';
    }

    textarea.addEventListener('input', autoResize);

    // Optional: call it once on load
    autoResize();
});
