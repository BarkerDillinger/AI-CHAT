document.addEventListener("DOMContentLoaded", () => {
    console.log("[CopyButton] DOM ready");

    function addCopyButtonToBlock(block) {
        if (block.querySelector(".copy-button")) return;

        const button = document.createElement("button");
        button.className = "copy-button";
        button.innerText = "📋";

        button.addEventListener("click", () => {
            let text = block.innerText || block.textContent;

            // Remove the emoji from any text and trim extra lines
            text = text.replace(/📋/g, "").trim();

            console.log("[CopyButton] Attempting to copy sanitized text:", text.slice(0, 40));

            if (!navigator.clipboard) {
                console.warn("[CopyButton] Clipboard API not supported");
                alert("Clipboard not supported in this browser.");
                return;
            }

            navigator.clipboard.writeText(text).then(() => {
                console.log("[CopyButton] Copied successfully");
                button.innerText = "✅";
                setTimeout(() => (button.innerText = "📋"), 1500);
            }).catch((err) => {
                console.error("[CopyButton] Copy failed", err);
                alert("Failed to copy: " + err.message);
            });
        });

        block.style.position = "relative";
        button.style.position = "absolute";
        button.style.top = "5px";
        button.style.right = "5px";
        button.style.padding = "4px 6px";
        button.style.background = "#222";
        button.style.color = "#00FF00";
        button.style.border = "1px solid #00FF00";
        button.style.fontSize = "0.8em";
        button.style.cursor = "pointer";
        button.style.zIndex = "10";

        block.appendChild(button);
    }

    function scanForCodeBlocks() {
        const blocks = document.querySelectorAll(".markdown-response pre");
        blocks.forEach(addCopyButtonToBlock);
    }

    scanForCodeBlocks();

    const observer = new MutationObserver(scanForCodeBlocks);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Modify full output and latest response copy behavior as well
    const sanitizeText = (text) => text.replace(/📋/g, "").trim();

    const copyAllBtn = document.getElementById("copy-entire-output");
    if (copyAllBtn) {
        copyAllBtn.addEventListener("click", () => {
            const blocks = document.querySelectorAll(".markdown-response.ai-response");
            let allText = "";
            blocks.forEach(block => {
                allText += sanitizeText(block.innerText || block.textContent) + "\n\n";
            });

            navigator.clipboard.writeText(allText.trim()).then(() => {
                console.log("[CopyAll] Entire output copied");
                copyAllBtn.innerText = "✅ Copied!";
                setTimeout(() => (copyAllBtn.innerText = "📄 Copy Full AI Output"), 1500);
            }).catch(err => {
                console.error("[CopyAll] Failed to copy full output", err);
                alert("Failed to copy: " + err.message);
            });
        });
    }

    const copyLatestBtn = document.getElementById("copy-latest-response");
    if (copyLatestBtn) {
        copyLatestBtn.addEventListener("click", () => {
            const lastPair = document.querySelectorAll(".conversation-pair");
            if (lastPair.length === 0) {
                alert("No responses to copy.");
                return;
            }

            const last = lastPair[lastPair.length - 1];
            const aiResponse = last.querySelector(".markdown-response.ai-response");

            if (!aiResponse) {
                alert("Could not find latest AI response.");
                return;
            }

            const text = sanitizeText(aiResponse.innerText || aiResponse.textContent);
            navigator.clipboard.writeText(text).then(() => {
                console.log("[CopyLatest] Copied last AI response");
                copyLatestBtn.innerText = "✅ Copied!";
                setTimeout(() => (copyLatestBtn.innerText = "📄"), 1500);
            }).catch(err => {
                console.error("[CopyLatest] Copy failed", err);
                alert("Copy failed: " + err.message);
            });
        });
    }
});
