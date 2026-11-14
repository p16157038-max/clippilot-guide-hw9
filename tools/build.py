"""Validate the single content source, then generate portable static pages."""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'slug', 'title', 'category', 'summary', 'audience', 'materials', 'shots', 'checks', 'related', 'updated', 'provenance'}
CATEGORIES = ('商品展示', '使用情境', '上市宣傳')


def validate(docs):
    slugs = [d.get('slug') for d in docs]
    if len(slugs) != len(set(slugs)):
        raise ValueError('slug 重複')
    for d in docs:
        slug = d.get('slug', '')
        if set(d) != FIELDS:
            raise ValueError(f'{slug} 欄位不符合 schema')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', slug):
            raise ValueError('slug 格式錯誤')
        if d['category'] not in CATEGORIES:
            raise ValueError(f'{slug} 分類錯誤')
        for field in ('title', 'summary', 'audience', 'provenance'):
            if not isinstance(d[field], str) or not d[field].strip():
                raise ValueError(f'{slug} {field} 不可空白')
        datetime.date.fromisoformat(d['updated'])
        if '原創示例，AI 協作撰寫' not in d['provenance']:
            raise ValueError(f'{slug} 缺少來源說明')
        for field, minimum, maximum in [('materials', 3, 5), ('checks', 4, 6)]:
            if not isinstance(d[field], list) or not minimum <= len(d[field]) <= maximum:
                raise ValueError(f'{slug} {field} 數量錯誤')
            if not all(isinstance(x, str) and x.strip() for x in d[field]):
                raise ValueError(f'{slug} {field} 包含空值')
        if not isinstance(d['shots'], list) or len(d['shots']) != 5:
            raise ValueError(f'{slug} 必須五格分鏡')
        for shot in d['shots']:
            if set(shot) != {'seconds', 'visual', 'caption'} or type(shot['seconds']) is not int or shot['seconds'] < 1:
                raise ValueError(f'{slug} 分鏡欄位或秒數錯誤')
            if not all(isinstance(shot[k], str) and shot[k].strip() for k in ('visual', 'caption')):
                raise ValueError(f'{slug} 分鏡內容空白')
            if len(shot['caption']) > 18:
                raise ValueError(f'{slug} 字幕超過 18 字')
        if sum(s['seconds'] for s in d['shots']) != 15:
            raise ValueError(f'{slug} 分鏡總秒數必須為 15')
        if not isinstance(d['related'], list) or len(d['related']) != 2 or len(set(d['related'])) != 2:
            raise ValueError(f'{slug} 必須兩個不重複相關指南')
        if any(x == slug or x not in slugs for x in d['related']):
            raise ValueError(f'{slug} 相關指南不存在或指向自己')
        if re.search(r'<[^>]+>', json.dumps(d, ensure_ascii=False)):
            raise ValueError(f'{slug} 內容不可含 HTML 標籤')


def e(value):
    return html.escape(str(value), quote=True)


def illustration(n=0):
    colors = ['#d8e7df', '#f3d6c5', '#dae1ef', '#e7dcbd', '#d4e5e2']
    return f'''<svg viewBox="0 0 240 180" role="img" aria-label="商品拍攝構圖示意，非實際商品照片"><rect width="240" height="180" rx="16" fill="{colors[n % 5]}"/><path d="M0 140Q110 115 240 142V180H0Z" fill="#fff" opacity=".4"/><ellipse cx="120" cy="143" rx="48" ry="9" fill="#162a2a" opacity=".1"/><rect x="88" y="53" width="65" height="86" rx="12" fill="#f8f5ee" stroke="#17685d" stroke-width="3"/><path d="M153 71h12a20 20 0 0 1 0 40h-12" fill="none" stroke="#17685d" stroke-width="7"/><path d="M101 79h39M101 91h25" stroke="#de693f" stroke-width="4" stroke-linecap="round"/><circle cx="205" cy="28" r="8" fill="#de693f"/><path d="M15 40V20h20M205 160h20v-20" fill="none" stroke="#17685d" stroke-width="2"/></svg>'''


def page(title, body, prefix=''):
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="ClipPilot 創作指南，提供 15 秒商品短影片的素材清單、五格分鏡與拍攝檢查。"><title>{e(title)} | ClipPilot 創作指南</title><link rel="stylesheet" href="{prefix}assets/site.css"><script defer src="{prefix}assets/site.js"></script></head>
<body><a class="skip-link" href="#main">跳至主要內容</a><header class="site-header wrap"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">C<span>▶</span></span><span>ClipPilot<small>創作指南</small></span></a><nav class="nav" aria-label="主要導覽"><a href="{prefix}index.html#library">指南庫</a><a href="{prefix}maintenance/index.html">規則與維護</a></nav></header><main id="main">{body}</main><footer class="wrap"><span>ClipPilot 創作指南 · 原創教學示例</span><a href="{prefix}maintenance/index.html">閱讀規則與 AI 協作說明 ↗</a></footer></body></html>'''


def card(d, n, prefix=''):
    tags = ''.join(f'<span>{s["seconds"]}s</span>' for s in d['shots'])
    return f'''<article class="guide-card" data-title="{e(d['title'])}" data-category="{e(d['category'])}" data-search="{e(d['title'] + ' ' + d['summary'] + ' ' + d['audience'])}"><div class="card-top"><span class="card-number">GUIDE / {n:02}</span><span class="tag">{e(d['category'])}</span></div><h3><a class="card-link" href="{prefix}guides/{d['slug']}/index.html">{e(d['title'])}<span aria-hidden="true"> ↗</span></a></h3><p>{e(d['summary'])}</p><div class="mini-shots" aria-label="五格秒數">{tags}<b>15 秒</b></div><span class="card-bottom">素材清單 · 五格分鏡 · 交付檢查</span></article>'''


def home(docs):
    art = ''.join(f'<div class="hero-frame">{illustration(i)}<span>0{i+1} / {label}</span></div>' for i, label in enumerate(['吸引注意', '展示細節', '留下行動']))
    filters = '<button class="filter active" type="button" data-filter="all" aria-pressed="true">全部指南</button>' + ''.join(f'<button class="filter" type="button" data-filter="{c}" aria-pressed="false">{c}</button>' for c in CATEGORIES)
    body = f'''<section class="hero wrap"><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">SMALL SHOP · BIG IDEAS</p><h1>把好商品，<br>說成一段好故事<span>。</span></h1><p class="lead">給小店店主的短影片拍攝指南。從素材到字幕，用五個畫面，把 15 秒安排清楚。</p><a class="primary-link" href="#library">找一份適合你的腳本 <span aria-hidden="true">↘</span></a><div class="hero-meta"><span class="pill">15 秒</span><span class="pill">五格分鏡</span><span class="pill">可直接照著拍</span></div></div><div class="hero-art"><div class="art-label">YOUR NEXT STORY / 你的下一段故事</div>{art}<p>構圖示意 · 請替換成自己的實際商品素材</p></div></div></section>
<section class="wrap library" id="library"><div class="section-head"><div><p class="eyebrow">THE PLAYBOOK</p><h2>選一個情境，開始拍。</h2></div><p>每篇都沿用同一套清楚的創作步驟。</p></div><div class="library-tools"><label for="search">搜尋指南<input id="search" type="search" placeholder="試試「開箱」或「飲品」" autocomplete="off"></label><div id="filters" aria-label="依情境篩選">{filters}</div></div><p id="result-count" aria-live="polite">共 {len(docs)} 篇指南</p><div id="guide-grid">{''.join(card(d, i+1) for i, d in enumerate(docs))}</div><p id="no-results" hidden>沒有符合的指南。試試其他關鍵字或選擇全部指南。</p></section>
<section class="wrap method"><div class="section-head"><div><p class="eyebrow">A REPEATABLE WORKFLOW</p><h2>內容增加，規則繼續沿用。</h2></div></div><div class="rules-grid"><article class="rule-card"><b>01 / 先讀規則</b><p>讀取 AGENTS.md，知道要做什麼、資料放哪裡，以及完成標準。</p></article><article class="rule-card"><b>02 / 補一份內容</b><p>依固定格式寫素材、五格分鏡與檢查項目。</p></article><article class="rule-card"><b>03 / 驗證再發布</b><p>建置器檢查欄位、15 秒與關聯，自動更新目錄與新頁面。</p></article></div><a class="text-link" href="maintenance/index.html">看這個網站如何持續擴充 ↗</a></section>'''
    return page('商品短影片拍攝指南', body)


def detail(d, docs):
    elapsed = 0
    shots = []
    lines = [d['title'], '素材：' + '、'.join(d['materials'])]
    for i, s in enumerate(d['shots']):
        time = f'{elapsed:02}–{elapsed+s["seconds"]:02} 秒'
        elapsed += s['seconds']
        shots.append(f'<article class="shot"><div class="shot-index">SHOT 0{i+1}<span class="seconds">{time}</span></div><div class="shot-art">{illustration(i)}</div><div class="shot-copy"><p>{e(s["visual"])}</p><p class="caption"><small>畫面字幕</small>{e(s["caption"])}</p></div></article>')
        lines.append(f'{time}｜{s["visual"]} 字幕：{s["caption"]}')
    lines.append('檢查：' + '；'.join(d['checks']))
    brief = '\n'.join(lines)
    related = [x for x in docs if x['slug'] in d['related']]
    body = f'''<article class="article wrap"><a class="back-link" href="../../index.html#library">← 返回指南庫</a><header class="article-head"><p class="eyebrow">CLIPPILOT PLAYBOOK / {e(d['category'])}</p><h1>{e(d['title'])}</h1><p class="lead">{e(d['summary'])}</p><div class="meta"><span class="pill">15 秒 · 五格分鏡</span><span>更新 {e(d['updated'])}</span></div></header><div class="intro-grid"><section><h2>這份指南適合誰</h2><p>{e(d['audience'])}</p><p class="notice">以下是拍攝腳本與構圖示意。請使用自己的實際素材，價格與商品資訊由店主確認。</p></section><section class="materials"><h2>先準備這些素材</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in d['materials'])}</ul></section></div><section><div class="section-head"><div><p class="eyebrow">YOUR 15 SECONDS</p><h2>照著五格，排好這段故事。</h2></div></div><div class="shots">{''.join(shots)}</div></section><section class="check-section"><h2>交付前，再看一次</h2><p>逐項確認後勾選；此裝置會嘗試記住勾選狀態。</p><div class="checklist">{''.join(f'<label><input type="checkbox" data-check="{i}"><span>{e(c)}</span></label>' for i,c in enumerate(d['checks']))}</div><p id="check-status" aria-live="polite">已確認 0 / {len(d['checks'])} 項</p></section><section class="brief-section"><div class="section-head"><h2>帶走這份拍攝摘要</h2><button id="copy-brief" type="button">複製摘要</button></div><pre id="brief">{e(brief)}</pre><p id="copy-status" role="status"></p></section><p class="provenance">{e(d['provenance'])}</p><section class="related"><h2>接著試試這些情境</h2><div class="rules-grid">{''.join(card(x,i+1,'../../') for i,x in enumerate(related))}</div></section></article>'''
    return page(d['title'], body, '../../')


def maintenance():
    body = '''<article class="article wrap"><a class="back-link" href="../index.html">← 返回首頁</a><header class="article-head"><p class="eyebrow">HOW WE KEEP BUILDING</p><h1>讓下一篇指南，沿用同一套方法。</h1><p class="lead">AGENTS.md 是 AI 接手前要讀的專案工作手冊。它說明目的、結構、內容格式與驗收方式，讓新內容可以持續增加。</p></header><section><h2>從規則到網頁的對應</h2><div class="rules-grid"><article class="rule-card"><b>內容與命名</b><p>content/&lt;slug&gt;.json 對應 guides/&lt;slug&gt;/index.html。英文小寫識別碼讓檔案、連結與首頁一致。</p></article><article class="rule-card"><b>統一的五格分鏡</b><p>每篇五格，時間總計 15 秒，每格字幕最多 18 字。建置器先檢查，再產生可讀頁面。</p></article><article class="rule-card"><b>固定版型</b><p>用途、素材、分鏡、檢查與摘要依固定順序呈現。全站沿用繁體中文與共用樣式。</p></article><article class="rule-card"><b>可持續新增</b><p>AI 讀手冊和範本後只新增一份來源檔；重新建置即可同步更新首頁、分類與指南頁。</p></article></div></section><section><h2>交給下一位 AI 的任務範例</h2><pre class="code">先讀 AGENTS.md 和 README.md。\n依 templates/guide.json 新增一篇文具商品指南。\n只新增內容來源，不修改共用樣式或其他指南。\n執行 build.py 與 check_site.py，回報變更及結果。</pre><p>如需變更分類或資料格式，應同步修改規則、範本和驗證器，避免文件與實作脫節。</p></section><section><h2>本次擴充與查證檔案</h2><p>可直接開啟原始規則、內容範本及實際擴充紀錄，對照網站上的新增指南。</p><ul><li><a href="../AGENTS.md">AGENTS.md 專案規則</a></li><li><a href="../templates/guide.json">guide.json 內容範本</a></li><li><a href="../evidence/extension-task.md">實際交辦給 AI 的擴充任務</a></li><li><a href="../evidence/extension-result.md">AI 擴充結果與檢查紀錄</a></li><li><a href="../CHANGELOG.md">CHANGELOG.md 修改紀錄</a></li></ul></section><section><h2>AI 協作與來源</h2><p>學生提出作業需求、品質與交付目標。AI 協助規則、原創指南、程式與檢查，另由獨立 AI 讀取規則執行新增指南。人類可依規則與來源檔逐項審查；這不是模型訓練，也沒有宣稱全部程式由學生手寫。</p><p>參考課堂「09 換你當老闆」與<a href="https://diveai-lab.github.io/diveai-lessons/">呆一布講義</a>的專案手冊思路。本站的主題、原創內容與視覺自行建立。所有商品情境為示例，正式資訊須由店主確認。</p></section></article>'''
    return page('規則與維護', body, '../')


def build():
    docs = []
    for p in sorted((ROOT / 'content').glob('*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        if p.stem != d.get('slug'):
            raise ValueError(f'{p.name} 檔名與 slug 不符')
        docs.append(d)
    if len(docs) < 1:
        raise ValueError('至少需要一篇指南')
    validate(docs)
    # Validation finishes before any output is written.
    (ROOT / 'index.html').write_text(home(docs), encoding='utf-8')
    for d in docs:
        target = ROOT / 'guides' / d['slug']
        target.mkdir(parents=True, exist_ok=True)
        (target / 'index.html').write_text(detail(d, docs), encoding='utf-8')
    target = ROOT / 'maintenance'
    target.mkdir(exist_ok=True)
    (target / 'index.html').write_text(maintenance(), encoding='utf-8')
    print(f'PASS: {len(docs)} source guides validated; {len(docs)+2} HTML pages built; all storyboards total 15 seconds.')


if __name__ == '__main__':
    build()
