/* All guide content is present in HTML. These enhancements are optional. */
(() => {
  "use strict";

  const ready = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  };

  ready(() => {
    const normalize = (value) => String(value || "").normalize("NFKC").toLocaleLowerCase("zh-Hant").trim();
    const search = document.getElementById("search");
    const filters = Array.from(document.querySelectorAll("#filters button[data-filter]"));
    const cards = Array.from(document.querySelectorAll("#guide-grid .guide-card"));
    const resultCount = document.getElementById("result-count");
    const noResults = document.getElementById("no-results");
    let category = filters.find((button) => button.classList.contains("active"))?.dataset.filter || "all";

    const filterCards = () => {
      const words = normalize(search?.value).split(/\s+/u).filter(Boolean);
      let count = 0;
      cards.forEach((card) => {
        const text = normalize([card.dataset.title, card.dataset.category, card.dataset.search, card.textContent].join(" "));
        const matches = (category === "all" || card.dataset.category === category) && words.every((word) => text.includes(word));
        card.hidden = !matches;
        if (matches) count += 1;
      });
      filters.forEach((button) => {
        const active = button.dataset.filter === category;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      if (resultCount) resultCount.textContent = `顯示 ${count} 篇指南，共 ${cards.length} 篇`;
      if (noResults) noResults.hidden = count !== 0;
    };

    if (cards.length) {
      search?.addEventListener("input", filterCards);
      search?.addEventListener("search", filterCards);
      filters.forEach((button) => button.addEventListener("click", () => {
        category = button.dataset.filter || "all";
        filterCards();
      }));
      filterCards();
    }

    const checks = Array.from(document.querySelectorAll('.checklist input[type="checkbox"]'));
    const checkStatus = document.getElementById("check-status");
    const storageKey = `clip-pilot:checks:${window.location.pathname}`;
    if (checks.length) {
      try {
        const saved = JSON.parse(window.localStorage.getItem(storageKey) || "null");
        if (Array.isArray(saved)) checks.forEach((check, index) => { check.checked = saved[index] === true; });
      } catch (_) {
        // Storage may be unavailable; checkboxes still work for this visit.
      }
      const updateChecks = () => {
        const done = checks.filter((check) => check.checked).length;
        if (checkStatus) checkStatus.textContent = done === checks.length
          ? `已完成 ${done}／${checks.length} 項交付檢查。`
          : `已完成 ${done}／${checks.length} 項檢查`;
      };
      checks.forEach((check) => check.addEventListener("change", () => {
        updateChecks();
        try {
          window.localStorage.setItem(storageKey, JSON.stringify(checks.map((item) => item.checked)));
        } catch (_) {
          // A blocked or full storage area must not interrupt the checklist.
        }
      }));
      updateChecks();
    }

    const copyButton = document.getElementById("copy-brief");
    const brief = document.getElementById("brief");
    const copyStatus = document.getElementById("copy-status");
    if (copyButton && brief) {
      const copyFallback = (text) => {
        const field = document.createElement("textarea");
        field.value = text;
        field.setAttribute("readonly", "");
        field.setAttribute("aria-label", "拍攝摘要複製暫存");
        field.style.cssText = "position:fixed;top:0;left:0;width:1px;height:1px;padding:0;border:0;opacity:0;pointer-events:none;";
        document.body.appendChild(field);
        let copied = false;
        const focused = document.activeElement;
        try {
          field.focus({ preventScroll: true });
          field.select();
          copied = typeof document.execCommand === "function" && document.execCommand("copy");
        } catch (_) {
          copied = false;
        } finally {
          field.remove();
          if (focused && typeof focused.focus === "function") focused.focus({ preventScroll: true });
        }
        return copied;
      };
      copyButton.addEventListener("click", async () => {
        const text = brief.textContent || "";
        let copied = false;
        copyButton.disabled = true;
        if (copyStatus) copyStatus.textContent = "正在複製摘要……";
        try {
          if (window.navigator.clipboard?.writeText) {
            try {
              await window.navigator.clipboard.writeText(text);
              copied = true;
            } catch (_) {
              copied = copyFallback(text);
            }
          } else {
            copied = copyFallback(text);
          }
        } catch (_) {
          copied = false;
        } finally {
          copyButton.disabled = false;
          if (copyStatus) copyStatus.textContent = copied
            ? "已複製拍攝摘要，可貼到備忘錄。"
            : "無法自動複製，請選取上方摘要文字後手動複製。";
        }
      });
    }
  });
})();
