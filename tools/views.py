"""Shared static views for the three-step shooting worksheet workflow."""
import html
import json


def e(value):
    return html.escape(str(value), quote=True)


GOALS = {
    'product-reveal': ('介紹商品外觀', '拍清楚包裝、細節與實際用法。', '帆布托特包', '', '內袋可收納鑰匙'),
    'daily-scenario': ('示範商品怎麼用', '用一個日常動作，交代商品的用法。', '隨行保溫杯', '', '單手按壓開蓋'),
    'feature-comparison': ('比較兩種款式', '用相同鏡位拍兩款，讓觀眾看懂差異。', '奶油白款', '森林綠款', '白款素面，綠款條紋'),
    'drink-launch': ('介紹飲品新品', '安排亮相、細節與結尾邀請。', '檸檬氣泡飲', '', '透明杯身看得見氣泡'),
}


def goal(d):
    fallback = (d['title'], d['summary'], '款式一' if d['slug'].endswith('-comparison') else '示範商品', '款式二' if d['slug'].endswith('-comparison') else '', '兩款可從實拍看見的差異' if d['slug'].endswith('-comparison') else '可從實拍看見的細節')
    return GOALS.get(d['slug'], fallback)


def page(title, body, prefix=''):
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="選拍攝目的、填商品資料，帶走五個鏡頭的15秒商品拍攝單。"><title>{e(title)} | ClipPilot 商品拍攝單</title><link rel="stylesheet" href="{prefix}assets/site.css"><script defer src="{prefix}assets/worksheet.js"></script><script defer src="{prefix}assets/site.js"></script></head>
<body><a class="skip-link" href="#main">跳至主要內容</a><header class="site-header wrap"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">C<span>▶</span></span><span>ClipPilot<small>商品拍攝單</small></span></a><nav class="nav" aria-label="主要導覽"><a href="{prefix}index.html#library">選拍攝目的</a><a href="{prefix}index.html#how-to">怎麼使用</a></nav></header><main id="main">{body}</main><footer class="wrap"><span>ClipPilot · 給小店店主的拍攝準備工具</span><a href="{prefix}maintenance/index.html">專案規則與 AI 協作說明</a></footer></body></html>'''


def card(d, n, prefix=''):
    title, description, *_ = goal(d)
    return f'''<article class="guide-card"><div class="card-top"><span class="card-number">{n:02}</span><span class="tag">{e(d['category'])}</span></div><h3><a class="card-link" href="{prefix}guides/{d['slug']}/index.html">{e(title)}<span aria-hidden="true"> →</span></a></h3><p>{e(description)}</p><p class="card-outcome">拿到：五個鏡頭、秒數與字幕</p></article>'''


def home(docs):
    ordered = sorted(docs, key=lambda d: (list(GOALS).index(d['slug']) if d['slug'] in GOALS else len(GOALS), d['slug']))
    sample = [('00–02 秒', '商品登場', '拍出帆布托特包的完整外觀'), ('02–05 秒', '展示包裝', '固定鏡位，拍下拆開包裝的過程'), ('05–08 秒', '拍一個細節', '靠近拍內袋如何收納鑰匙'), ('08–12 秒', '示範使用', '錄下拿取物品與背起包包的動作'), ('12–15 秒', '結尾邀請', '商品與店名同框，邀請到店看看')]
    sample_rows = ''.join(f'<div class="sample-row"><span class="sample-time">{t}</span><div class="sample-text"><b>{a}</b><span>{b}</span></div></div>' for t, a, b in sample)
    body = f'''<section class="hero wrap"><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">給第一次拍商品影片的你</p><h1>不知道先拍什麼？<br>先拿一張 15 秒拍攝單。</h1><p class="lead">選一個拍攝目的，填商品名稱與一個真實特徵，取得五個鏡頭的拍法、秒數與字幕。</p><a class="primary-link" href="#library">開始做我的拍攝單 →</a><a class="secondary-link" href="guides/product-reveal/index.html?example=1#worksheet-result">先用帆布包範例試一次</a><p class="scope-note">完成後用手機照著拍，再依秒數與順序放進你慣用的剪輯工具。這裡交付的是拍攝單。</p></div><div class="hero-art sample-sheet"><div class="sample-sheet-head"><span class="tag">完成後會拿到什麼</span><h2>帆布托特包的拍攝單</h2><p>範例 · 五鏡共 15 秒</p></div>{sample_rows}<p class="sample-note">每個鏡頭都有拍法與字幕，可複製或下載文字檔。</p></div></div></section>
<section class="wrap" id="how-to"><div class="section-head"><div><h2>三步完成，帶去現場拍。</h2></div></div><div class="how-steps"><article class="step"><span>1</span><h3>選拍攝目的</h3><p>決定這支影片要介紹外觀、示範用法、比較款式，還是介紹新品。</p></article><article class="step"><span>2</span><h3>填商品資料</h3><p>填名稱、已確認的特徵與結尾行動。也可以先用範例看結果。</p></article><article class="step"><span>3</span><h3>帶走拍攝單</h3><p>確認五個鏡頭後複製或下載，照著拍攝，再依順序剪接。</p></article></div></section>
<section class="wrap library" id="library"><div class="section-head"><div><p class="eyebrow">從這裡開始</p><h2>這次，你想讓觀眾看懂什麼？</h2></div></div><div class="goal-grid">{''.join(card(d, i+1) for i,d in enumerate(ordered))}</div></section>'''
    return page('15 秒商品拍攝單', body)


def detail(d, docs):
    title, description, sample_name, sample_variant, sample_feature = goal(d)
    comparison = d['slug'].endswith('-comparison')
    name_label = '款式一名稱' if comparison else '商品名稱'
    name_placeholder = f'例如：{sample_name}'
    variant = '<label for="variant-name">款式二名稱 <span>必填，最多 12 字</span><input id="variant-name" name="variant" required maxlength="12" placeholder="例如：森林綠款" autocomplete="off"></label>' if comparison else ''
    elapsed, shots, lines = 0, [], [d['title'], '素材：' + '、'.join(d['materials'])]
    for i, s in enumerate(d['shots']):
        time = f'{elapsed:02}–{elapsed+s["seconds"]:02} 秒'
        elapsed += s['seconds']
        shots.append(f'<article class="shot" data-index="{i}"><div class="shot-index">第 {i+1} 鏡<span class="seconds">{time}</span></div><div class="shot-copy"><small class="shot-label">怎麼拍</small><p data-shot-visual>{e(s["visual"])}</p><p class="caption"><small>畫面上的字</small><strong data-shot-caption>{e(s["caption"])}</strong></p></div></article>')
        lines.append(f'{time}｜{s["visual"]} 字幕：{s["caption"]}')
    lines.append('檢查：' + '；'.join(d['checks']))
    brief = '\n'.join(lines)
    raw_data = json.dumps(d, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')
    body = f'''<article class="article wrap"><a class="back-link" href="../../index.html#library">← 換一個拍攝目的</a><header class="article-head"><p class="eyebrow">已選擇：{e(title)}</p><h1>{e(title)}的 15 秒拍攝單</h1><p class="lead">{e(d["summary"])} 填入自己的商品資料，讓下方拍攝單變成這次能用的版本。</p></header><ol class="guide-progress" aria-label="使用步驟"><li><a href="../../index.html#library">1 選拍攝目的</a></li><li>2 填商品資料</li><li>3 複製或下載拍攝單</li></ol>
<section id="worksheet" class="worksheet-layout"><div class="worksheet-inputs"><h2>填入這次要拍的商品</h2><p>個人化依固定範本整理；請填你已確認的商品資訊。</p><form id="worksheet-form" data-mode="{'comparison' if comparison else 'single'}"><label for="product-name">{name_label} <span>必填，最多 12 字</span><input id="product-name" name="name" required maxlength="12" placeholder="{name_placeholder}" autocomplete="off"></label>{variant}<label for="product-feature">想拍清楚的一個特徵 <span>選填，最多 18 字</span><input id="product-feature" name="feature" maxlength="18" placeholder="例如：{e(sample_feature)}" autocomplete="off"></label><p class="field-help">寫實際看得到、拍得到的細節。留白就沿用範例中的中性說法。</p><label for="ending-action">結尾希望觀眾做什麼<select id="ending-action" name="action"><option>到店看看實品</option><option>私訊詢問商品</option><option>查看商品資訊</option></select></label><div class="form-actions"><button type="submit">更新拍攝單</button><button id="use-example" type="button" data-example-name="{e(sample_name)}" data-example-variant="{e(sample_variant)}" data-example-feature="{e(sample_feature)}">先填入範例</button></div><p id="sheet-feedback" role="status" aria-live="polite">還沒填資料？可以先按「先填入範例」看看。</p></form><noscript><p>目前仍可閱讀下方範例拍攝單；個人化、複製與下載需要啟用 JavaScript。</p></noscript><div class="worksheet-help"><h3>拿到拍攝單後怎麼做？</h3><p>準備下方素材，拿手機逐鏡拍攝；再把五段畫面放入慣用的剪輯工具，依標示時間裁切、加上字幕，完成 15 秒影片。</p></div></div></section>
<section id="worksheet-result" class="worksheet-result" aria-labelledby="sheet-product"><div class="result-head"><div><p class="eyebrow">你的交付成果</p><h2 id="sheet-product">{e(d['title'])}範例拍攝單</h2><p id="sheet-notice" role="status">目前是通用範例。填資料後按「更新拍攝單」，這裡就會更新。</p><a class="edit-link" href="#worksheet">修改商品資料 ↑</a></div><div class="sheet-actions"><button id="copy-brief" type="button">複製拍攝單</button><button id="download-brief" type="button">下載文字檔</button></div></div><p class="sheet-time">共 5 個鏡頭 · 合計 15 秒 · 字幕可直接帶去剪輯</p><div class="shots">{''.join(shots)}</div><p id="copy-status" role="status"></p><details class="brief-section"><summary>查看可複製與下載的完整文字</summary><pre id="brief">{e(brief)}</pre></details></section>
<section class="preparation"><div class="materials"><h2>拍攝前要準備</h2><p>{e(d["audience"])}</p><ul>{''.join('<li>'+e(x)+'</li>' for x in d['materials'])}</ul></div><div class="check-section"><h2>拍完後，確認這些事</h2><div class="checklist">{''.join(f'<label><input type="checkbox" data-check="{i}"><span>{e(c)}</span></label>' for i,c in enumerate(d['checks']))}</div><p id="check-status" aria-live="polite">已確認 0 / {len(d['checks'])} 項</p></div></section><p class="provenance">{e(d['provenance'])}</p></article><script id="guide-data" type="application/json">{raw_data}</script>'''
    return page(title + '拍攝單', body, '../../')


def maintenance():
    body = '''<article class="article wrap"><a class="back-link" href="../index.html">← 返回拍攝工具</a><header class="article-head"><p class="eyebrow">給專案維護者與作業審閱者</p><h1>用同一套規則，繼續新增拍攝範本。</h1><p class="lead">使用者的工作是選範本、填資料、帶走拍攝單。維護者的工作則是依 AGENTS.md 新增內容，沿用同一套介面與驗證方式。</p></header><section><h2>規則如何對應到產品</h2><div class="rules-grid"><article class="rule-card"><h3>先寫內容來源</h3><p>每篇 content/&lt;slug&gt;.json 記錄素材、五個鏡頭、字幕與檢查。建置器驗證五格合計 15 秒後，產生對應網頁。</p></article><article class="rule-card"><h3>沿用共用使用流程</h3><p>新範本會自動有商品資料表單與拍攝單。商品名稱、已確認特徵與結尾行動實際更新鏡頭，複製與下載採用同一份文字。</p></article><article class="rule-card"><h3>驗收實際輸出</h3><p>檢查來源與頁面一致、連結有效，再檢查一般商品、兩款比較、空白特徵、長度限制與文字安全。網站沒有呼叫模型 API。</p></article></div></section><section><h2>可交給下一位 AI 的任務</h2><pre class="code">先讀 AGENTS.md、README.md 與一篇既有來源。\n依 templates/guide.json 新增一篇文具商品拍攝範本。\n沿用五格十五秒、繁體中文與共用介面。\n執行建置、網站與拍攝單規則檢查，記錄結果。</pre><p>一般新增範本只新增內容來源，無須改共用版型。變更資料格式或介面時，需同步更新規則、範本與檢查工具。</p></section><section><h2>規則、來源與實際證據</h2><ul><li><a href="../AGENTS.md">完整 AGENTS.md 規則</a></li><li><a href="../templates/guide.json">新內容的 JSON 範本</a></li><li><a href="../evidence/extension-task.md">11 月 14 日獨立 AI 擴充任務</a></li><li><a href="../evidence/extension-result.md">當時版本的擴充結果</a></li><li><a href="../evidence/usability-update.json">11 月 15 日使用流程改版與當前檢查</a></li><li><a href="../CHANGELOG.md">修改紀錄</a></li></ul><p>舊版擴充的雜湊以對應 Git 提交為準，當前介面改版另記結果。</p></section><section><h2>AI 協作與教材來源</h2><p>學生提出需求並指出使用目的與流程不清楚的問題；AI 協助規則、範本、程式與檢查，依回饋改成可帶去拍攝的工作單。獨立 AI 擴充紀錄保留實際交辦與輸出。</p><p>參考教師「09 換你當老闆」與<a href="https://diveai-lab.github.io/diveai-lessons/">呆一布講義</a>的專案規則設計。本站內容為原創教學情境，實際商品資訊由使用者確認。</p></section></article>'''
    return page('專案規則與 AI 協作', body, '../')
