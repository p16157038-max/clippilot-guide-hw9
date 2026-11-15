"""Statically check source parity, worksheet markup and portable links.

These checks parse HTML only. They do not claim browser interaction, clipboard,
download, layout or accessibility testing.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Parser(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.lang = ''
        self.links = []
        self.ids = []
        self.elements = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        index = len(self.elements)
        self.elements.append({'tag': tag, 'attrs': a,
                              'parents': tuple(self.stack), 'text': ''})
        if tag not in self.VOID:
            self.stack.append(index)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'html':
            self.lang = a.get('lang', '')
        if 'id' in a:
            self.ids.append(a['id'])
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.elements[self.stack[i]]['tag'] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        for index in self.stack:
            self.elements[index]['text'] += data

    def by_id(self, value):
        matches = [x for x in self.elements if x['attrs'].get('id') == value]
        assert len(matches) == 1, f'Expected exactly one #{value}'
        return matches[0]

    def inside(self, parent, tag=None, css_class=None):
        parent_index = self.elements.index(parent)
        return [x for x in self.elements
                if parent_index in x['parents']
                and (tag is None or x['tag'] == tag)
                and (css_class is None or css_class in x['attrs'].get('class', '').split())]


def check_scripts(parser):
    scripts = [x for x in parser.elements
               if x['tag'] == 'script' and 'src' in x['attrs']]
    for name in ('worksheet.js', 'site.js'):
        matches = [x for x in scripts if x['attrs']['src'].endswith('/' + name)]
        assert len(matches) == 1, f'Expected one {name} script'
        assert 'defer' in matches[0]['attrs'], f'{name} must be deferred'
    names = [x['attrs']['src'].rsplit('/', 1)[-1] for x in scripts]
    assert names.index('worksheet.js') < names.index('site.js'), 'Worksheet must load before site enhancements'


def check_guide(parser, doc):
    form = parser.by_id('worksheet-form')
    assert form['tag'] == 'form', 'Worksheet entry must be a form'
    comparison = doc['slug'].endswith('-comparison')
    assert form['attrs'].get('data-mode') == ('comparison' if comparison else 'single')
    data = parser.by_id('guide-data')
    assert data['tag'] == 'script' and data['attrs'].get('type') == 'application/json'
    assert json.loads(data['text']) == doc, f'{doc["slug"]}: embedded data does not match source'

    for attr, source_key in [('data-shot-visual', 'visual'), ('data-shot-caption', 'caption')]:
        nodes = [x for x in parser.elements if attr in x['attrs']]
        assert len(nodes) == 5, f'{doc["slug"]}: expected five {attr} nodes'
        assert [x['text'].strip() for x in nodes] == [s[source_key] for s in doc['shots']], \
            f'{doc["slug"]}: static shot content differs from source'

    controls = parser.inside(form)
    for name, maximum, required in [('product-name', '12', True), ('product-feature', '18', False)]:
        field = parser.by_id(name)
        assert field in controls and field['tag'] == 'input', f'#{name} must be inside the form'
        assert field['attrs'].get('maxlength') == maximum, f'#{name} length limit'
        assert ('required' in field['attrs']) is required, f'#{name} required status'
    variants = [x for x in parser.elements if x['attrs'].get('id') == 'variant-name']
    assert len(variants) == int(comparison), 'Second variant exists only for comparison'
    if comparison:
        variant = variants[0]
        assert variant in controls and variant['tag'] == 'input'
        assert 'required' in variant['attrs'] and variant['attrs'].get('maxlength') == '12'
    action = parser.by_id('ending-action')
    assert action in controls and action['tag'] == 'select'
    assert len(parser.inside(action, tag='option')) >= 1, 'CTA choices missing'
    for name in ('copy-brief', 'download-brief'):
        button = parser.by_id(name)
        assert button['tag'] == 'button' and button['attrs'].get('type') == 'button', f'#{name} must be a button'
    brief = parser.by_id('brief')
    assert brief['tag'] == 'pre' and brief['text'].strip(), 'Readable copy/download sheet missing'
    assert len(parser.inside(form, tag='button')) >= 2, 'Update and example actions missing'


def check_home(parser, docs):
    assert 'search' not in parser.ids and 'filters' not in parser.ids, 'Four-goal home should not use search/filter controls'
    assert not any(x['tag'] == 'input' and x['attrs'].get('type') == 'search'
                   for x in parser.elements), 'Search input still present'
    goal_grids = [x for x in parser.elements if 'goal-grid' in x['attrs'].get('class', '').split()]
    assert len(goal_grids) == 1, 'Expected one purpose selection grid'
    cards = parser.inside(goal_grids[0], tag='article', css_class='guide-card')
    assert len(cards) == len(docs), 'Every source needs a purpose card'
    hrefs = []
    for card in cards:
        links = parser.inside(card, tag='a')
        assert len(links) == 1, 'Each goal needs one direct guide link'
        hrefs.append(links[0]['attrs'].get('href'))
    assert set(hrefs) == {f'guides/{d["slug"]}/index.html' for d in docs}, 'Goal links do not match guides'
    how_to = parser.by_id('how-to')
    steps = parser.inside(how_to, tag='article', css_class='step')
    assert len(steps) == 3, 'Expected three visible usage steps'
    headings = [''.join(x['text'] for x in parser.inside(step, tag='h3')) for step in steps]
    assert headings == ['選拍攝目的', '填商品資料', '帶走拍攝單'], 'Usage steps should explain the task in order'


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
        check_scripts(parser)
        parsed[p.resolve()] = parser
    check_home(parsed[(ROOT / 'index.html').resolve()], docs)
    for doc in docs:
        check_guide(parsed[(ROOT / 'guides' / doc['slug'] / 'index.html').resolve()], doc)
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
    print(f'PASS: {len(pages)} pages; {len(docs)} source/output pairs; {count} local targets; zh-Hant; one H1 per page; no duplicate IDs; worksheet forms/data/5 shots/limits/actions/scripts; three-step purpose home. Static HTML checks only, not browser interaction tests.')


if __name__ == '__main__':
    check()
