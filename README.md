# ClipPilot 商品拍攝單

第九週作業 1103：建立自己的 AGENTS.md。

這是給小店店主的 15 秒商品拍攝單工具。解決「不知道影片要拍什麼、每鏡放多久、字幕寫什麼」的準備問題。選拍攝目的、填商品資料，就能取得五個鏡頭的拍法、秒數與字幕，複製或下載成文字檔。

## 第一次使用

1. 在首頁選「介紹商品外觀」；也可直接按「先用帆布包範例試一次」。
2. 填入「帆布托特包」、特徵「內袋可收納鑰匙」，選「到店看看實品」，按「更新拍攝單」。
3. 看開場、細節與結尾是否出現自己的資料，再複製或下載拍攝單。拿手機照五鏡拍攝，最後用慣用剪輯工具依秒數裁切與加字幕。

比較兩款時需填兩個款式名稱。沒有填特徵就保留中性範本內容。個人化使用瀏覽器中的固定範本組合，沒有在網站呼叫 AI、上傳照片或生成影片；商品資料不送往伺服器。

線上網站：https://p16157038-max.github.io/clippilot-guide-hw9/

GitHub 原始碼：https://github.com/p16157038-max/clippilot-guide-hw9

專案規則：https://github.com/p16157038-max/clippilot-guide-hw9/blob/main/AGENTS.md

## 閱讀與維護

AI 接手前先讀根目錄 `AGENTS.md`。正式範本來自 `content/*.json`；`tools/build.py` 驗證後，透過 `tools/views.py` 產生首頁、拍攝單與維護頁。新增一篇符合規則的來源檔後重建，即可自動加入入口，沿用同一套表單與拍攝單介面。

```sh
python tools/build.py
python tools/check_site.py
python tools/test_rules.py
node tools/test_worksheet.cjs
python -m http.server 8019
```

建置使用 Python 3.10 以上，拍攝單邏輯檢查使用 Node.js；兩者均無額外套件。開啟終端顯示的 localhost 連結瀏覽。也可直接開啟根目錄 `index.html`，主要範例已產生為靜態 HTML，個人化與匯出需要 JavaScript。

## 發布 GitHub Pages

將整個專案（包括 `AGENTS.md`、來源、工具與輸出）上傳 GitHub。repository 的 Settings → Pages → Deploy from a branch，選 `main` 分支與 `/ (root)`，儲存後等待部署。所有內部連結均為相對路徑，支援 repository 子路徑。

## 如何驗證本次作業

1. 開首頁，能看懂三步操作、交付成果與後續手機拍攝方式。
2. 用上述帆布包案例，確認資料真的進入鏡頭與字幕，五格合計 15 秒，複製與下載和畫面相同。
3. 讀根目錄 `AGENTS.md`，對照素材數量、五格 schema、命名、目錄、驗證流程與網頁。
4. 讀 `evidence/` 的擴充交辦與結果。11 月 14 日新增第四篇的紀錄屬歷史版本；11 月 15 日使用流程改版另記於 `usability-update.json`，不將舊雜湊當成當前檔案。

## 教材參考與 AI 協作

參考教師提供的「09 換你當老闆」與 https://diveai-lab.github.io/diveai-lessons/ 的專案規則設計方式（目的、結構、內容先行、命名與交接）。本站自行設計主題、規則與畫面，沒有複製該站內容、品牌或素材。

學生提出作業需求、品質與交付目標；AI 協助規則、內容、程式與檢查，另由獨立 AI 執行受限擴充。這是程式與文件協作，不是訓練模型。實際分工及檢查紀錄在 `evidence/`；不得宣稱學生手寫所有程式或已做未記錄的測試。
