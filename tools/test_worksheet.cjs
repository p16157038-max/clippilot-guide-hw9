"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { createSheet, validateInputs } = require("../assets/worksheet.js");
const source = (slug) => JSON.parse(fs.readFileSync(path.join(__dirname, "..", "content", `${slug}.json`), "utf8"));
const product = source("product-reveal");
const comparison = source("feature-comparison");
const actual = { name: "帆布托特包", feature: "內袋可收納鑰匙", action: "到店看看實品" };

test("real product, visible feature and ending update their actual shots and exported text", () => {
  const result = createSheet(product, actual);
  assert.match(result.shots[0].visual, /帆布托特包/);
  assert.match(result.shots[0].caption, /帆布托特包/);
  assert.match(result.shots[2].visual, /內袋可收納鑰匙/);
  assert.equal(result.shots[2].caption, actual.feature);
  assert.match(result.shots[4].visual, /到店看看實品/);
  assert.equal(result.shots[4].caption, actual.action);
  for (const value of Object.values(actual)) assert.ok(result.brief.includes(value));
});

test("all four sources keep exactly their five durations and fifteen seconds", () => {
  for (const slug of ["product-reveal", "daily-scenario", "feature-comparison", "drink-launch"]) {
    const guide = source(slug);
    const before = JSON.stringify(guide);
    const result = createSheet(guide, { ...actual, variant: "森林綠馬克杯" });
    assert.equal(result.shots.length, 5);
    assert.deepEqual(result.shots.map((shot) => shot.seconds), guide.shots.map((shot) => shot.seconds));
    assert.equal(result.shots.reduce((sum, shot) => sum + shot.seconds, 0), 15);
    assert.ok(result.shots.every((shot) => Array.from(shot.caption).length <= 18));
    assert.equal(JSON.stringify(guide), before, "source content must not be mutated");
  }
});

test("blank optional feature preserves the source's neutral third shot", () => {
  for (const slug of ["product-reveal", "daily-scenario", "drink-launch"]) {
    const guide = source(slug);
    const result = createSheet(guide, { name: "實際商品", feature: "", action: "查看商品資訊" });
    assert.deepEqual(result.shots[2], guide.shots[2]);
    assert.ok(!result.brief.includes("店主填寫的可見特徵"));
  }
});

test("comparison uses both real names in the corresponding fair-condition shots", () => {
  const result = createSheet(comparison, { name: "白色馬克杯", variant: "綠色馬克杯", feature: "", action: "私訊詢問商品" });
  assert.match(result.shots[0].visual, /白色馬克杯.*綠色馬克杯/);
  assert.equal(result.shots[0].caption, "白色馬克杯／綠色馬克杯");
  assert.match(result.shots[1].visual, /白色馬克杯/);
  assert.equal(result.shots[1].caption, "白色馬克杯");
  assert.match(result.shots[2].visual, /綠色馬克杯/);
  assert.equal(result.shots[2].caption, "綠色馬克杯");
  assert.match(result.shots[1].visual, /相同的光線、距離及使用條件/);
  assert.match(result.shots[2].visual, /相同鏡位、光線與距離/);
  assert.match(result.shots[4].visual, /白色馬克杯.*綠色馬克杯/);
});

test("comparison feature is explicitly checked against both products, without an invented winner", () => {
  const result = createSheet(comparison, { name: "白色馬克杯", variant: "綠色馬克杯", feature: "兩款都有提把" });
  assert.match(result.shots[2].visual, /須先核對.*分別實拍兩款/);
  assert.equal(result.shots[2].caption, "綠色馬克杯");
  assert.equal(result.shots[3].caption, "兩款都有提把");
  assert.match(result.shots[3].visual, /兩款都有提把/);
});

test("missing required names produce clear field errors; variant is required only for comparison", () => {
  assert.equal(validateInputs(product, { name: "" }).valid, false);
  assert.ok(validateInputs(product, { name: "" }).errors.name);
  assert.ok(validateInputs(comparison, { name: "白色馬克杯" }).errors.variant);
  assert.equal(validateInputs(product, { name: "帆布托特包" }).valid, true);
});

test("a new source-only comparison slug inherits the two-product workflow", () => {
  const futureGuide = { ...comparison, slug: "color-comparison" };
  assert.ok(validateInputs(futureGuide, { name: "白色馬克杯" }).errors.variant);
  const result = createSheet(futureGuide, { name: "白色馬克杯", variant: "綠色馬克杯" });
  assert.match(result.title, /白色馬克杯 × 綠色馬克杯/);
  assert.match(result.shots[1].visual, /白色馬克杯/);
  assert.match(result.shots[2].visual, /綠色馬克杯/);
});

test("overlong text is rejected, never shortened; exact limits remain intact", () => {
  for (const [field, length] of [["name", 13], ["variant", 13], ["feature", 19]]) {
    const input = { name: "白色馬克杯", variant: "綠色馬克杯", feature: "", [field]: "字".repeat(length) };
    assert.throws(() => createSheet(comparison, input), (error) => error.name === "WorksheetValidationError" && Boolean(error.fields[field]));
  }
  const result = createSheet(comparison, { name: "字".repeat(12), variant: "款".repeat(12), feature: "特".repeat(18) });
  assert.equal(result.shots[1].caption, "字".repeat(12));
  assert.equal(result.shots[0].caption, "兩款實拍比較");
  assert.equal(result.shots[2].caption, "款".repeat(12));
  assert.equal(result.shots[3].caption, "特".repeat(18));
  assert.ok(result.shots.every((shot) => Array.from(shot.caption).length <= 18));
});

test("action must be a listed choice and multiline fields are rejected", () => {
  assert.ok(validateInputs(product, { name: "商品", action: "保證買到最好" }).errors.action);
  assert.ok(validateInputs(product, { name: "商品\n下一行" }).errors.name);
});

test("markup-like input stays literal data in the sheet, including the complete exported text", () => {
  const literal = "<img src=x>";
  const result = createSheet(product, { name: literal, feature: "<b>細節</b>" });
  assert.ok(result.title.includes(literal));
  assert.ok(result.shots[0].visual.includes(literal));
  assert.equal(result.shots[2].caption, "<b>細節</b>");
  assert.ok(result.brief.includes(literal));
  assert.ok(result.brief.includes("<b>細節</b>"));
});

test("brief uses LF consistently and includes every visible shot and caption", () => {
  const result = createSheet(product, actual);
  assert.ok(!result.brief.includes("\r"));
  assert.ok(result.brief.startsWith(result.title + "\n"));
  for (const shot of result.shots) {
    assert.ok(result.brief.includes(shot.visual));
    assert.ok(result.brief.includes(`字幕：${shot.caption}`));
  }
});

test("invalid source timing fails rather than exporting an incorrect fifteen-second sheet", () => {
  const guide = structuredClone(product);
  guide.shots[0].seconds = 9;
  assert.throws(() => createSheet(guide, actual), /合計 15 秒/);
});
