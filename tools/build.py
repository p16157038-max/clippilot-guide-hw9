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


from views import page, card, home, detail, maintenance


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
