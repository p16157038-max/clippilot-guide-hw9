# ClipPilot 創作指南

第九週作業 1103：建立自己的 AGENTS.md。

這是給小店店主的商品短影片指南網站。每篇有素材清單、15 秒五格分鏡、字幕與交付檢查。網站以繁體中文提供可閱讀、可搜尋、可複製摘要的教學內容，不需要 API key。

## 閱讀與維護

AI 接手前先讀根目錄 `AGENTS.md`。正式內容來自 `content/*.json`；`tools/build.py` 負責驗證並產生首頁、指南頁與維護說明頁。新增一篇符合規則的來源檔後重建，即可自動加入首頁與分類，不需逐頁改版型。

```sh
python tools/build.py
python tools/check_site.py
python -m http.server 8019
```

Python 3.10 以上，僅用標準函式庫，無額外套件。開啟終端顯示的 localhost 連結瀏覽。也可直接開啟根目錄 `index.html`，主要內容已產生為靜態 HTML。

## 發布 GitHub Pages

將整個專案（包括 `AGENTS.md`、來源、工具與輸出）上傳 GitHub。repository 的 Settings → Pages → Deploy from a branch，選 `main` 分支與 `/ (root)`，儲存後等待部署。所有內部連結均為相對路徑，支援 repository 子路徑。

## 如何驗證本次作業

1. 開首頁，使用分類與搜尋找指南。
2. 開任一指南，看五格時間總計 15 秒、勾選檢查並複製摘要。
3. 讀根目錄 `AGENTS.md`，對照素材數量、五格 schema、命名、目錄、驗證流程與網頁。
4. 讀 `evidence/` 的擴充交辦與結果，查看新增指南的來源及實際檢查輸出。

## 教材參考與 AI 協作

參考教師提供的「09 換你當老闆」與 https://diveai-lab.github.io/diveai-lessons/ 的專案規則設計方式（目的、結構、內容先行、命名與交接）。本站自行設計主題、規則與畫面，沒有複製該站內容、品牌或素材。

學生提出作業需求、品質與交付目標；AI 協助規則、內容、程式與檢查，另由獨立 AI 執行受限擴充。這是程式與文件協作，不是訓練模型。實際分工及檢查紀錄在 `evidence/`；不得宣稱學生手寫所有程式或已做未記錄的測試。
