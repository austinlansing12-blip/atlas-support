import unittest

from test_static_site_contract import PAGES, REPO_ROOT, normalize_text, parse_page


class StaticPageAccessibilityTests(unittest.TestCase):
    def test_each_page_has_one_main_region_and_ordered_headings(self):
        for page_key in PAGES:
            with self.subTest(page=page_key):
                page = parse_page(page_key)
                self.assertEqual(page.tag_counts.get("main", 0), 1)
                self.assertGreaterEqual(len(page.headings), 1)
                self.assertEqual(page.headings[0]["tag"], "h1")

                for heading in page.headings:
                    self.assertTrue(heading["text"])

                h1_count = sum(1 for heading in page.headings if heading["tag"] == "h1")
                self.assertEqual(h1_count, 1)

    def test_links_have_readable_text_and_no_blank_target_without_rel(self):
        generic_link_text = {"click here", "here", "learn more", "read more"}

        for page_key in PAGES:
            page = parse_page(page_key)
            for link in page.links:
                href = link["attrs"].get("href", "")
                text = normalize_text("".join(link["text_parts"]))

                with self.subTest(page=page_key, href=href):
                    self.assertTrue(href)
                    self.assertTrue(text)
                    self.assertNotIn(text.lower(), generic_link_text)

                    if link["attrs"].get("target") == "_blank":
                        rel_tokens = set(link["attrs"].get("rel", "").lower().split())
                        self.assertIn("noopener", rel_tokens)

    def test_layout_css_preserves_mobile_readability_basics(self):
        required_css_fragments = [
            "color-scheme: light dark",
            "line-height:",
            "max-width:",
            "padding:",
            "letter-spacing: 0",
        ]

        for page_key, relative_path in PAGES.items():
            source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(page=page_key):
                self.assertIn("<style>", source)
                for fragment in required_css_fragments:
                    self.assertIn(fragment, source)

    def test_policy_and_support_share_core_safety_disclaimer(self):
        expected_fragments = [
            "not a medical device",
            "does not provide medical advice, diagnosis, or treatment",
        ]

        for page_key in ("privacy", "support"):
            text = parse_page(page_key).text.lower()
            for fragment in expected_fragments:
                with self.subTest(page=page_key, fragment=fragment):
                    self.assertIn(fragment, text)

    def test_secondary_pages_include_multiple_scan_friendly_sections(self):
        for page_key in ("privacy", "support", "community"):
            page = parse_page(page_key)
            with self.subTest(page=page_key):
                self.assertGreaterEqual(len(page.heading_texts("h2")), 3)
                self.assertTrue(page.text.startswith("Atlas"))


if __name__ == "__main__":
    unittest.main()
