# 獨立 AI 擴充結果

日期：2026-11-14。這是獨立 AI 實際執行 `evidence/extension-task.md` 的紀錄，非模擬對話或預先宣稱通過的測試。

已讀 `AGENTS.md`、`README.md`、`CHANGELOG.md`、`templates/guide.json` 及既有的 `content/product-reveal.json`。新增 `content/drink-launch.json`，其餘內容來源、共用樣式與工具不修改。

## 實際變更

- 新增 `content/drink-launch.json`：分類為上市宣傳，五項素材、五格分鏡、六項檢查、兩個既有相關指南及原創來源說明。
- 由原有工具新增 `guides/drink-launch/index.html`，更新首頁 `index.html` 的目錄與總篇數，沒有手改產生的 HTML。
- 更新本結果檔，並於 `CHANGELOG.md` 追加此次工作與實際檢查。
- 建置前是三份內容來源、三個指南頁；建置後是四份內容來源、四個指南頁，連同首頁與維護頁共六頁。建置工具會重寫全部六頁，既有三個指南頁與維護頁的內容沒有差異。

## 規則如何落實

1. 先讀規則、說明、修改紀錄、範本及既有指南，再依固定欄位撰寫 JSON；檔名與 slug 同為 `drink-launch`。
2. 使用臺灣繁體中文與全形中文標點，分類沿用「上市宣傳」，未新增 schema 或共用版型。
3. 五格為 2、3、3、4、3 秒，合計 15 秒；字幕分別為 6、7、6、7、8 個字元，均不超過 18。素材五項、檢查六項，符合規定數量。
4. 情境明示為虛構小店；未捏造價格、成分、折扣、上架日期或其他商品事實。待確認資訊要求由店主核對，尚未確認就不上畫面，沒有品牌抄寫、成效承諾或虛構見證。
5. 檢查包含實際飲品、品名、素材權利與入鏡同意等事實核對。`related` 使用現有且不是自己的 `product-reveal` 與 `daily-scenario`。
6. 唯一新增的正式內容來源是 `content/drink-launch.json`。三份既有來源、`assets/` 與 `tools/` 均未修改，以原有工具先驗證後建置，再檢查來源與輸出對應。

## 實際執行與輸出

所有命令在專案根目錄執行，使用以下既有 Python（以下以 `PYTHON` 簡記這個完整路徑，並非另裝執行環境）：

```text
C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe
```

執行 `PYTHON -X utf8 tools/build.py`，結束碼 0：

```text
PASS: 4 source guides validated; 6 HTML pages built; all storyboards total 15 seconds.
```

執行 `PYTHON -X utf8 tools/check_site.py`，結束碼 0：

```text
PASS: 6 pages; 4 source/output pairs; 66 local targets; zh-Hant; one H1 per page; no duplicate IDs.
```

另以同一 Python 的標準函式庫實際讀取來源與產生頁面，逐一比對文字、首頁連結、分鏡卡片數量及檔案雜湊，結束碼 0：

```text
PASS: all 8 protected file hashes match baseline.
PASS: baseline-hashes.json unchanged; SHA-256 43b03c0f3608a906930f6636a66ae75d0b37a68c1dba68fe2a8a2dd7d14a2dcd
PASS: home links to drink-launch; 4 guides displayed; new page contains all source text and 5 storyboard cards.
PASS: seconds=2,3,3,4,3; total=15; caption lengths=6,7,6,7,8
Final counts: 4 sources; 4 guide pages; 6 total HTML pages.
```

比對的八個受保護檔案是：`assets/site.css`、`assets/site.js`、`content/daily-scenario.json`、`content/feature-comparison.json`、`content/product-reveal.json`、`tools/build.py`、`tools/check_site.py`、`tools/test_rules.py`。擴充前後均與 `evidence/baseline-hashes.json` 所列 SHA-256 相符，雜湊清單檔本身也保持相同。

## 尚未執行的檢查與交接

本次交辦禁止瀏覽器呼叫、上傳與外部 API，因此未操作瀏覽器、未啟動預覽伺服器，也未發布或提交 Git。390px 手機寬度、視覺排版、鍵盤焦點、停用 JavaScript 的實際瀏覽、搜尋無結果、分類篩選、複製摘要與清單勾選，皆未在本次擴充測試驗證，不能據此宣稱通過。靜態頁面的內容文字與結構、語言、H1、來源輸出數量及相對連結已由上列實際程式檢查通過；後續可由主工作流程另外操作瀏覽器驗證。
