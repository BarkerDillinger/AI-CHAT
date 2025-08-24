// static/scripts/contextDelete.js

console.log("contextDelete.js loaded");

(() => {
  const MENU_ID = "convo-context-menu";

  // ---------- utils ----------
  function setSidebarLinksEnabled(enabled) {
    document.querySelectorAll("#conversation-list a").forEach(a => {
      a.style.pointerEvents = enabled ? "auto" : "none";
    });
  }

  function ensureMenu() {
    let m = document.getElementById(MENU_ID);
    if (m) return m;

    m = document.createElement("div");
    m.id = MENU_ID;
    m.style.position = "fixed";
    m.style.minWidth = "180px";
    m.style.padding = "8px 0";
    m.style.background = "rgba(28,28,28,0.98)";
    m.style.border = "1px solid #444";
    m.style.borderRadius = "8px";
    m.style.boxShadow = "0 6px 24px rgba(0,0,0,0.4)";
    m.style.zIndex = 9999;
    m.style.display = "none";
    m.innerHTML = `
      <button data-action="delete" class="ctx-item" style="width:100%;text-align:left;padding:8px 12px;background:none;border:none;cursor:pointer">
        🗑️ Delete conversation
      </button>
    `;
    document.body.appendChild(m);

    // Handle clicks INSIDE the menu first (action handler)
    m.addEventListener("click", async (e) => {
      const btn = e.target.closest(".ctx-item[data-action='delete']");
      if (!btn) return;

      e.preventDefault();
      e.stopPropagation();

      const id = m.dataset.convoId;
      const title = m.dataset.convoTitle || `Conversation ${id}`;
      hideMenu();

      if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;

      try {
        await delConvo(id);
        document.querySelector(`.conversation-item[data-convo-id="${id}"]`)?.remove();
        if (document.body.dataset.conversationId === id) window.location.href = "/";
      } catch (err) {
        console.error(err);
        alert("Failed to delete conversation. Reloading to resync.");
        window.location.reload();
      }
    });

    // Hide on clicks OUTSIDE the menu
    document.addEventListener("click", (e) => {
      if (!m || m.style.display === "none") return;
      if (!m.contains(e.target)) hideMenu();
    }, { passive: true });

    // Hide on scroll/resize
    window.addEventListener("scroll", hideMenu, { passive: true });
    window.addEventListener("resize", hideMenu);

    return m;
  }

  function showMenu(x, y, ctx) {
    const m = ensureMenu();
    m.style.left = Math.max(0, x) + "px";
    m.style.top = Math.max(0, y) + "px";
    m.dataset.convoId = ctx.convoId;
    m.dataset.convoTitle = ctx.title || `Conversation ${ctx.convoId}`;
    m.style.display = "block";
    setSidebarLinksEnabled(false);
  }

  function hideMenu() {
    const m = document.getElementById(MENU_ID);
    if (m) m.style.display = "none";
    setSidebarLinksEnabled(true);
  }

  async function delConvo(id) {
    const res = await fetch(`/conversation/${id}`, { method: "DELETE" });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`DELETE /conversation/${id} -> ${res.status} ${res.statusText} ${text}`);
    }
  }

  // ---------- desktop right-click ----------
  document.addEventListener("contextmenu", (e) => {
    const item = e.target.closest(".conversation-item");
    if (!item) return;
    e.preventDefault();
    showMenu(e.clientX, e.clientY, {
      convoId: item.dataset.convoId,
      title: item.dataset.convoTitle
    });console.log("contextDelete.js loaded");
  });

  // ---------- mobile long-press ----------
  let touchTimer = null;
  document.addEventListener("touchstart", (e) => {
    const item = e.target.closest(".conversation-item");
    if (!item || e.touches.length !== 1) return;
    const t = e.touches[0];
    touchTimer = setTimeout(() => {
      showMenu(t.clientX, t.clientY, {
        convoId: item.dataset.convoId,
        title: item.dataset.convoTitle
      });
    }, 550);
  }, { passive: true });

  document.addEventListener("touchmove", () => {
    if (touchTimer) { clearTimeout(touchTimer); touchTimer = null; }
  }, { passive: true });

  document.addEventListener("touchend", () => {
    if (touchTimer) { clearTimeout(touchTimer); touchTimer = null; }
  }, { passive: true });

  // ---------- keyboard delete (focus a sidebar item, press Delete) ----------
  document.addEventListener("keydown", async (e) => {
    if (e.key !== "Delete") return;
    const item = document.activeElement?.closest?.(".conversation-item");
    if (!item) return;
    const id = item.dataset.convoId;
    const title = item.dataset.convoTitle || `Conversation ${id}`;
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) return;

    try {
      await delConvo(id);
      item.remove();
      if (document.body.dataset.conversationId === id) window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert("Failed to delete conversation. Reloading to resync.");
      window.location.reload();
    }
  });
})();
