import unittest

from research.collector.benchmark import JS_HTML, STATIC_HTML_TEMPLATE, _extract_static_ids


class CollectorBenchmarkExtractorTests(unittest.TestCase):
    def test_static_html_finds_only_visible_fixture_records(self) -> None:
        self.assertEqual(["post-001"], _extract_static_ids(STATIC_HTML_TEMPLATE.format(id="post-001")))

    def test_javascript_string_is_not_mistaken_for_a_static_record(self) -> None:
        self.assertEqual([], _extract_static_ids(JS_HTML))


if __name__ == "__main__":
    unittest.main()
