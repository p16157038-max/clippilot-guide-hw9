/* Pure worksheet logic, shared by the browser and the Node acceptance checks. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ClipPilotWorksheet = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const ACTIONS = Object.freeze(["到店看看實品", "私訊詢問商品", "查看商品資訊"]);
  const LIMITS = Object.freeze({ name: 12, variant: 12, feature: 18 });
  const fieldLabels = { name: "商品名稱", variant: "第二款名稱", feature: "可見特徵" };
  const count = (text) => Array.from(text).length;
  const isComparison = (guide) => Boolean(guide && typeof guide.slug === "string" && guide.slug.endsWith("-comparison"));

  function validateInputs(guide, values) {
    const input = values && typeof values === "object" ? values : {};
    const data = {};
    const errors = {};
    for (const field of Object.keys(LIMITS)) {
      const raw = input[field] === undefined ? "" : input[field];
      if (typeof raw !== "string") {
        data[field] = "";
        errors[field] = `請以文字填寫${fieldLabels[field]}。`;
        continue;
      }
      data[field] = raw.trim();
      if (/[\u0000-\u001f\u007f]/u.test(raw)) {
        errors[field] = `${fieldLabels[field]}請使用單行文字。`;
      } else if (count(data[field]) > LIMITS[field]) {
        errors[field] = `${fieldLabels[field]}最多 ${LIMITS[field]} 個字，請縮短後再更新。`;
      }
    }
    if (!data.name && !errors.name) errors.name = "請填寫你要拍攝的商品名稱。";
    if (isComparison(guide) && !data.variant && !errors.variant) errors.variant = "比較兩款商品時，請填寫第二款名稱。";
    if (!isComparison(guide)) {
      data.variant = "";
      delete errors.variant;
    }
    data.action = input.action === undefined ? ACTIONS[0] : input.action;
    if (!ACTIONS.includes(data.action)) errors.action = "請從清單選擇結尾行動。";
    return { valid: Object.keys(errors).length === 0, data, errors };
  }

  function validateGuide(guide) {
    if (!guide || typeof guide.title !== "string" || !Array.isArray(guide.materials) || !Array.isArray(guide.checks)
      || !Array.isArray(guide.shots) || guide.shots.length !== 5
      || guide.shots.some((shot) => !shot || !Number.isInteger(shot.seconds) || shot.seconds < 1
        || typeof shot.visual !== "string" || typeof shot.caption !== "string")
      || guide.shots.reduce((total, shot) => total + shot.seconds, 0) !== 15) {
      throw new TypeError("這份來源必須包含五格、合計 15 秒的有效拍攝內容。");
    }
  }

  function createSheet(guide, values) {
    validateGuide(guide);
    const validation = validateInputs(guide, values);
    if (!validation.valid) {
      const error = new Error(Object.values(validation.errors).join(" "));
      error.name = "WorksheetValidationError";
      error.fields = validation.errors;
      throw error;
    }
    const { name, variant, feature, action } = validation.data;
    const shots = guide.shots.map((shot) => ({ seconds: shot.seconds, visual: shot.visual, caption: shot.caption }));
    let title = `${name}｜15 秒拍攝單`;

    if (isComparison(guide)) {
      title = `${name} × ${variant}｜15 秒比較拍攝單`;
      shots[0].visual = `將「${name}」與「${variant}」並排放好，在相同背景、光線與距離下拍清楚兩款外觀。`;
      const pairCaption = `${name}／${variant}`;
      shots[0].caption = count(pairCaption) <= 18 ? pairCaption : "兩款實拍比較";
      shots[1].visual = `固定鏡位拍「${name}」的外觀與可見細節，保持與下一格相同的光線、距離及使用條件。`;
      shots[1].caption = name;
      shots[2].visual = `以相同鏡位、光線與距離拍「${variant}」，只呈現可實拍的差異，不加入優劣評語。`;
      shots[2].caption = variant;
      if (feature) {
        shots[2].visual += ` 差異「${feature}」須先核對，再分別實拍兩款對應位置，不能只替其中一款加效果。`;
        shots[3].visual = `將「${name}」與「${variant}」在相同場景與條件下使用，實拍已核對的差異「${feature}」，不加入未確認的優劣評語。`;
        shots[3].caption = feature;
      }
      shots[4].visual = `讓「${name}」與「${variant}」回到同條件並排畫面，搭配店名與「${action}」；聯絡方式確認後再放上畫面。`;
    } else {
      const opening = {
        "product-reveal": `將「${name}」的完整包裝放在乾淨桌面，手從側邊入鏡，保留商品真實外觀。`,
        "daily-scenario": `在「${name}」實際使用的日常場景拍攝，讓商品與場景同框，交代接下來要做的動作。`,
        "drink-launch": `將「${name}」從畫面側邊放到桌面中央，完整呈現實際杯身與外觀。`
      };
      shots[0].visual = opening[guide.slug] || `將「${name}」放入畫面，先拍清楚實際商品的完整外觀。`;
      shots[0].caption = `先看${name}`;
      if (feature) {
        shots[2].visual = `靠近拍「${name}」的可見特徵「${feature}」，以實際商品畫面核對；需要示範時拍完整動作，不用剪接暗示未確認功效。`;
        shots[2].caption = feature;
      }
      shots[4].visual = `讓「${name}」與店名同框，字幕寫「${action}」；店名、聯絡方式與商品資訊確認後才放上畫面。`;
    }
    shots[4].caption = action;

    let elapsed = 0;
    const lines = [title, `拍攝目標：${guide.title}`, `商品：${name}`];
    if (variant) lines.push(`第二款：${variant}`);
    if (feature) lines.push(`店主填寫的可見特徵（拍攝前核對）：${feature}`);
    lines.push(`結尾行動：${action}`, "", "先準備素材：", ...guide.materials.map((material) => `・${material}`), "", "五格分鏡：");
    for (const shot of shots) {
      const start = String(elapsed).padStart(2, "0");
      elapsed += shot.seconds;
      lines.push(`${start}–${String(elapsed).padStart(2, "0")} 秒｜${shot.visual}`, `字幕：${shot.caption}`, "");
    }
    lines.push("拍攝與交付前檢查：", ...guide.checks.map((check) => `□ ${check}`));
    return { title, shots, brief: lines.join("\n") };
  }

  return Object.freeze({ ACTIONS, LIMITS, isComparison, validateInputs, createSheet });
});
