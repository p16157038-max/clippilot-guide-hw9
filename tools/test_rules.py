"""Regression checks for documented content constraints and safe HTML output.

Run from the project root: python tools/test_rules.py
Only the standard library is used. The fixtures are independent of production
content so a changed guide cannot silently change the expected failure cases.
"""
import copy
import importlib.util
import unittest
from html.parser import HTMLParser
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "guide_build", Path(__file__).with_name("build.py")
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def fixture():
    docs = []
    slugs = ("alpha", "beta", "gamma")
    for slug in slugs:
        docs.append({
            "slug": slug,
            "title": "商品拍攝指南",
            "category": "商品展示",
            "summary": "用五個畫面清楚介紹商品。",
            "audience": "第一次拍攝的小店店主。",
            "materials": ["商品實拍", "使用情境", "店主確認的商品資訊"],
            "shots": [
                {"seconds": 3, "visual": "拍攝實際商品細節。", "caption": "看見生活細節"}
                for _ in range(5)
            ],
            "checks": ["核對商品資訊", "核對素材授權", "字幕可讀", "總長十五秒"],
            "related": [other for other in slugs if other != slug],
            "updated": "2026-11-14",
            "provenance": "原創示例，AI 協作撰寫；虛構情境，商品事實由店主核對。",
        })
    return docs


class ContentRulesTests(unittest.TestCase):
    def setUp(self):
        self.docs = fixture()

    def rejected(self, modify):
        docs = copy.deepcopy(self.docs)
        modify(docs[0])
        with self.assertRaises(ValueError):
            build.validate(docs)

    def test_valid_fifteen_second_fixture(self):
        build.validate(self.docs)

    def test_duration_must_total_fifteen(self):
        for seconds in (2, 4):
            with self.subTest(total=12 + seconds):
                self.rejected(lambda d: d["shots"][0].update(seconds=seconds))

    def test_each_shot_requires_positive_integer_duration(self):
        for value in (0, -1, 3.0, True, "3"):
            with self.subTest(seconds=value):
                self.rejected(lambda d: d["shots"][0].update(seconds=value))

    def test_exactly_five_shots(self):
        self.rejected(lambda d: d["shots"].pop())
        self.rejected(lambda d: d["shots"].append(copy.deepcopy(d["shots"][0])))

    def test_missing_and_unknown_top_level_fields(self):
        for key in sorted(build.FIELDS):
            with self.subTest(missing=key):
                self.rejected(lambda d: d.pop(key))
        self.rejected(lambda d: d.update(unexpected="不應接受此欄位"))

    def test_missing_and_unknown_shot_fields(self):
        for key in ("seconds", "visual", "caption"):
            with self.subTest(missing=key):
                self.rejected(lambda d: d["shots"][0].pop(key))
        self.rejected(lambda d: d["shots"][0].update(unexpected="額外欄位"))

    def test_slug_rejects_invalid_names_and_paths(self):
        for slug in ("Alpha", "alpha_beta", "../alpha", "alpha/child", "alpha beta", "alpha-", "商品", "", 123, None):
            with self.subTest(slug=slug):
                self.rejected(lambda d: d.update(slug=slug))

    def test_duplicate_slug_rejected(self):
        self.docs[1]["slug"] = "alpha"
        with self.assertRaises(ValueError):
            build.validate(self.docs)

    def test_related_rejects_self_missing_and_duplicate(self):
        for related in (["alpha", "beta"], ["beta", "missing-guide"], ["beta", "beta"], ["beta"], "beta"):
            with self.subTest(related=related):
                self.rejected(lambda d: d.update(related=related))

    def test_caption_length_boundary(self):
        self.docs[0]["shots"][0]["caption"] = "字" * 18
        build.validate(self.docs)
        self.rejected(lambda d: d["shots"][0].update(caption="字" * 19))

    def test_empty_caption_and_visual_rejected(self):
        for key in ("visual", "caption"):
            with self.subTest(field=key):
                self.rejected(lambda d: d["shots"][0].update({key: "  "}))

    def test_html_rejected_across_content_fields(self):
        mutations = {
            "title": lambda d: d.update(title="<script>alert(1)</script>"),
            "summary": lambda d: d.update(summary='<img src=x onerror="alert(1)">'),
            "materials": lambda d: d["materials"].__setitem__(0, "<b>素材</b>"),
            "visual": lambda d: d["shots"][0].update(visual="<svg onload=alert(1)>"),
            "caption": lambda d: d["shots"][0].update(caption="<b>字</b>"),
            "checks": lambda d: d["checks"].__setitem__(0, "<a href=x>檢查</a>"),
        }
        for field, mutation in mutations.items():
            with self.subTest(field=field):
                self.rejected(mutation)

    def test_category_provenance_and_count_constraints(self):
        self.rejected(lambda d: d.update(category="未定義分類"))
        self.rejected(lambda d: d.update(provenance="沒有指定來源說明"))
        self.rejected(lambda d: d.update(materials=["只有一項"]))
        self.rejected(lambda d: d.update(checks=["只有一項"]))


class HtmlEscapeTests(unittest.TestCase):
    def test_escape_handles_text_and_attribute_delimiters(self):
        self.assertEqual(
            build.e('<script a="x">&\'</script>'),
            "&lt;script a=&quot;x&quot;&gt;&amp;&#x27;&lt;/script&gt;",
        )

    def test_valid_plain_text_cannot_break_card_attributes(self):
        class MarkupParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.elements = []
                self.text = []

            def handle_starttag(self, tag, attrs):
                self.elements.append((tag, dict(attrs)))

            def handle_data(self, data):
                self.text.append(data)

        docs = fixture()
        malicious = '商品 " onmouseover="alert(1) & 春日'
        docs[0]["title"] = malicious
        build.validate(docs)
        output = build.card(docs[0], 1)
        parser = MarkupParser()
        parser.feed(output)
        self.assertIn(malicious, "".join(parser.text))
        self.assertIn('商品 &quot; onmouseover=&quot;alert(1) &amp; 春日', output)
        self.assertFalse(any(tag in ("script", "iframe", "object", "embed")
                             for tag, _ in parser.elements))
        self.assertFalse(any(name.lower().startswith("on")
                             for _, attrs in parser.elements for name in attrs))
        links = [attrs for tag, attrs in parser.elements if tag == "a"]
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["href"], "guides/alpha/index.html")

    def test_detail_escapes_plain_text_in_copyable_summary(self):
        docs = fixture()
        docs[0]["materials"][0] = '實拍照片 & 店主 "確認"'
        build.validate(docs)
        output = build.detail(docs[0], docs)
        self.assertIn("實拍照片 &amp; 店主 &quot;確認&quot;", output)
        self.assertNotIn('實拍照片 & 店主 "確認"', output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
