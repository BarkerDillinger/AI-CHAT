window.addEventListener('resize', () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    console.log(`New size: ${width}x${height}`);
    adjustTextSize(width);
});

function adjustTextSize(width) {
    const responseBox = document.getElementById('response-box');
    
    if (!responseBox) return;

    if (width < 500) {
        responseBox.style.fontSize = '14px';
    } else if (width < 900) {
        responseBox.style.fontSize = '16px';
    } else {
        responseBox.style.fontSize = '18px';
    }
}
