"""Check generated pages, local links, language and source/output parity."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.lang = ''
        self.links = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'html':
            self.lang = a.get('lang', '')
        if 'id' in a:
            self.ids.append(a['id'])
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])


def check():
    docs = [json.loads(p.read_text(encoding='utf-8')) for p in (ROOT / 'content').glob('*.json')]
    expected = {x['slug'] for x in docs}
    actual = {x.parent.name for x in (ROOT / 'guides').glob('*/index.html')}
    assert expected == actual, 'Guide source/output mismatch'
    pages = [ROOT / 'index.html', ROOT / 'maintenance/index.html'] + sorted((ROOT / 'guides').glob('*/index.html'))
    parsed = {}
    for p in pages:
        parser = Parser()
        parser.feed(p.read_text(encoding='utf-8'))
        assert parser.h1 == 1 and parser.lang == 'zh-Hant', str(p)
        assert len(parser.ids) == len(set(parser.ids)), f'Duplicate IDs in {p}'
        parsed[p.resolve()] = parser
    count = 0
    for p, parser in parsed.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            assert not url.path.startswith('/'), f'Absolute local URL: {link}'
            target = (p.parent / unquote(url.path)).resolve() if url.path else p
            assert target.is_relative_to(ROOT.resolve()) and target.exists(), f'Missing target {link} in {p}'
            if url.fragment and target in parsed:
                assert unquote(url.fragment) in parsed[target].ids, f'Missing anchor {link}'
            count += 1
    print(f'PASS: {len(pages)} pages; {len(docs)} source/output pairs; {count} local targets; zh-Hant; one H1 per page; no duplicate IDs.')


if __name__ == '__main__':
    check()
