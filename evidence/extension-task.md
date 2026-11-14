# 實際交辦的擴充任務

這是本次獨立 AI 擴充實驗的實際任務，不是學生與 AI 全部聊天的逐字紀錄。

## Prompt

請先閱讀專案根目錄的 AGENTS.md、README.md、CHANGELOG.md，以及 templates/guide.json 和一篇既有指南。

新增一篇「飲品新品上市」的 15 秒拍攝指南，slug 使用 drink-launch，分類使用上市宣傳。情境為虛構小店；價格、成分與折扣未提供，不得自行捏造。請包含五格分鏡、素材清單、可驗收檢查與來源說明。

只新增 content/drink-launch.json，不改任何既有指南、共用樣式或建置程式。執行 tools/build.py 與 tools/check_site.py，讓新頁面與首頁由既有系統產生。將實際變更與執行輸出寫入 evidence/extension-result.md，並在 CHANGELOG.md 增加紀錄。若檢查失敗，修正新增來源後再執行。

## 驗收

- 三篇既有指南的 JSON 與 assets、tools 檔案雜湊不變。
- 指南由三篇變成四篇，產生 guides/drink-launch/index.html。
- 首頁能連到新頁面，五格總計 15 秒，來源與網站內容相符。
- 保留實際檢查結果，不把推測寫成已通過。
