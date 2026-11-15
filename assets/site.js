/* The neutral worksheet remains readable when JavaScript is unavailable. */
(() => {
  "use strict";
  const ready = (fn) => document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", fn, { once: true }) : fn();

  ready(() => {
    const form = document.getElementById("worksheet-form");
    const brief = document.getElementById("brief");
    const copyStatus = document.getElementById("copy-status");
    const notice = document.getElementById("sheet-notice");
    const feedback = document.getElementById("sheet-feedback");
    const logic = window.ClipPilotWorksheet;
    const checks = Array.from(document.querySelectorAll('.checklist input[type="checkbox"]'));
    const checkStatus = document.getElementById("check-status");
    let guide = null;
    const updateChecks = () => {
      const done = checks.filter((check) => check.checked).length;
      if (checkStatus) checkStatus.textContent = `已完成 ${done}／${checks.length} 項檢查`;
    };
    checks.forEach((check) => check.addEventListener("change", updateChecks));
    if (checks.length) updateChecks();

    const dataElement = document.getElementById("guide-data");
    if (dataElement) {
      try { guide = JSON.parse(dataElement.textContent); } catch (_) { guide = null; }
    }

    if (form && guide && logic && brief) {
      const fields = {
        name: document.getElementById("product-name"),
        variant: document.getElementById("variant-name"),
        feature: document.getElementById("product-feature"),
        action: document.getElementById("ending-action")
      };
      const exampleButton = document.getElementById("use-example");
      const errorNodes = {};
      form.noValidate = true;
      if (fields.variant) fields.variant.required = logic.isComparison(guide);

      Object.entries(fields).forEach(([key, field]) => {
        if (!field) return;
        const error = document.createElement("span");
        error.id = `${field.id}-error`;
        error.className = "field-error";
        error.hidden = true;
        field.insertAdjacentElement("afterend", error);
        const describedBy = field.getAttribute("aria-describedby");
        field.setAttribute("aria-describedby", [describedBy, error.id].filter(Boolean).join(" "));
        errorNodes[key] = error;
      });

      const getValues = () => ({
        name: fields.name?.value || "",
        variant: fields.variant?.value || "",
        feature: fields.feature?.value || "",
        action: fields.action?.value || logic.ACTIONS[0]
      });
      const showErrors = (errors) => {
        Object.entries(fields).forEach(([key, field]) => {
          if (!field) return;
          const message = errors[key] || "";
          field.setCustomValidity(message);
          field.setAttribute("aria-invalid", String(Boolean(message)));
          if (errorNodes[key]) {
            errorNodes[key].textContent = message;
            errorNodes[key].hidden = !message;
          }
        });
      };
      const apply = (isSample) => {
        const validation = logic.validateInputs(guide, getValues());
        showErrors(validation.errors);
        if (!validation.valid) {
          if (feedback) feedback.textContent = "請修正標示的欄位，再更新拍攝單。";
          const first = Object.keys(validation.errors).map((key) => fields[key]).find(Boolean);
          first?.focus();
          return false;
        }
        try {
          const sheet = logic.createSheet(guide, validation.data);
          const productHeading = document.getElementById("sheet-product");
          const prefix = isSample ? "示例 SAMPLE｜" : "";
          if (productHeading) productHeading.textContent = prefix + sheet.title;
          const shotNodes = document.querySelectorAll("#worksheet-result .shot");
          shotNodes.forEach((node, fallbackIndex) => {
            const index = node.hasAttribute("data-index") ? Number(node.dataset.index) : fallbackIndex;
            const shot = sheet.shots[index];
            if (!shot) return;
            const visual = node.querySelector("[data-shot-visual]");
            const caption = node.querySelector("[data-shot-caption]");
            if (visual) visual.textContent = shot.visual;
            if (caption) caption.textContent = shot.caption;
          });
          brief.textContent = prefix + sheet.brief;
          if (notice) notice.textContent = isSample
            ? "示例 SAMPLE：這是示範商品資料。換成你的真實商品資訊後，再更新拍攝單。"
            : "已套用你填寫的商品資訊；拍攝前請核對可見特徵與聯絡方式。";
          if (feedback) feedback.textContent = "拍攝單已更新。五格內容、複製與下載已同步。";
          if (copyStatus) copyStatus.textContent = "";
          checks.forEach((check) => { check.checked = false; });
          if (checks.length) updateChecks();
          const result = document.getElementById("worksheet-result");
          const reduceMotion = typeof window.matchMedia === "function"
            && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
          if (typeof result?.scrollIntoView === "function") {
            result.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
          }
          if (productHeading) {
            productHeading.setAttribute("tabindex", "-1");
            productHeading.focus({ preventScroll: true });
          }
          return true;
        } catch (_) {
          if (feedback) feedback.textContent = "目前無法更新，請先使用下方原始拍攝單。";
          return false;
        }
      };

      Object.entries(fields).forEach(([key, field]) => {
        if (!field) return;
        const changed = () => {
          const validation = logic.validateInputs(guide, getValues());
          if (!validation.errors[key]) {
            field.setCustomValidity("");
            field.setAttribute("aria-invalid", "false");
            if (errorNodes[key]) errorNodes[key].hidden = true;
          }
          if (feedback) feedback.textContent = "欄位已變更。按「更新拍攝單」後，才會套用到五格與匯出內容。";
        };
        field.addEventListener("input", changed);
        field.addEventListener("change", changed);
      });
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        apply(false);
      });
      const useExample = () => {
        if (!exampleButton || !fields.name) return;
        fields.name.value = exampleButton.dataset.exampleName || "";
        if (fields.variant) fields.variant.value = exampleButton.dataset.exampleVariant || "";
        if (fields.feature) fields.feature.value = exampleButton.dataset.exampleFeature || "";
        apply(true);
      };
      exampleButton?.addEventListener("click", useExample);
      if (new URLSearchParams(window.location.search).get("example") === "1") useExample();
    } else if (form && (!guide || !logic)) {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (feedback) feedback.textContent = "目前無法更新，仍可閱讀、複製或下載下方原始拍攝單。";
      });
    }

    const copyFallback = (text) => {
      const field = document.createElement("textarea");
      field.value = text;
      field.setAttribute("readonly", "");
      field.setAttribute("aria-label", "拍攝單複製暫存");
      field.style.cssText = "position:fixed;top:0;left:0;width:1px;height:1px;padding:0;border:0;opacity:0;pointer-events:none;";
      document.body.appendChild(field);
      const focused = document.activeElement;
      let copied = false;
      try {
        field.focus({ preventScroll: true });
        field.select();
        copied = typeof document.execCommand === "function" && document.execCommand("copy");
      } catch (_) { copied = false; }
      finally {
        field.remove();
        if (focused && typeof focused.focus === "function") focused.focus({ preventScroll: true });
      }
      return copied;
    };
    const copyButton = document.getElementById("copy-brief");
    if (copyButton && brief) copyButton.addEventListener("click", async () => {
      const text = brief.textContent || "";
      let copied = false;
      copyButton.disabled = true;
      if (copyStatus) copyStatus.textContent = "正在複製拍攝單……";
      try {
        if (window.navigator.clipboard?.writeText) {
          try { await window.navigator.clipboard.writeText(text); copied = true; }
          catch (_) { copied = copyFallback(text); }
        } else copied = copyFallback(text);
      } catch (_) { copied = false; }
      finally {
        copyButton.disabled = false;
        if (copyStatus) copyStatus.textContent = copied
          ? "已複製拍攝單，可貼到備忘錄。"
          : "無法自動複製，請選取下方完整拍攝單後手動複製。";
      }
    });

    const downloadButton = document.getElementById("download-brief");
    if (downloadButton && brief) downloadButton.addEventListener("click", () => {
      let url;
      try {
        const slug = typeof guide?.slug === "string" && /^[a-z]+(?:-[a-z]+)*$/.test(guide.slug) ? guide.slug : "clippilot";
        const file = new Blob([brief.textContent || ""], { type: "text/plain;charset=utf-8" });
        url = URL.createObjectURL(file);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${slug}-shooting-sheet.txt`;
        link.hidden = true;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 30000);
        if (copyStatus) copyStatus.textContent = "已送出文字檔下載，請查看瀏覽器的下載紀錄。";
      } catch (_) {
        if (url) URL.revokeObjectURL(url);
        if (copyStatus) copyStatus.textContent = "無法下載，請複製或手動選取下方完整拍攝單。";
      }
    });
  });
})();
