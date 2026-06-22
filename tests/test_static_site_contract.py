from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]

PAGES = {
    "home": Path("index.html"),
    "privacy": Path("privacy/index.html"),
    "support": Path("support/index.html"),
}

EXPECTED_TITLES = {
    "home": "Atlas",
    "privacy": "Atlas Privacy Policy",
    "support": "Atlas Support",
}

EXPECTED_H1S = {
    "home": "Atlas",
    "privacy": "Atlas Privacy Policy",
    "support": "Atlas Support",
}

APPROVED_EXTERNAL_HOSTS = {
    "github.com",
}


def normalize_text(value):
    return " ".join(value.split())


class StaticPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.declarations = []
        self.html_attrs = {}
        self.metas = []
        self.navs = []
        self.links = []
        self.stylesheet_links = []
        self.tag_counts = {}
        self.title_parts = []
        self.body_text_parts = []
        self.headings = []
        self._in_body = False
        self._in_title = False
        self._active_link_indices = []
        self._heading_stack = []

    def handle_decl(self, decl):
        self.declarations.append(decl)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = {name.lower(): value for name, value in attrs}
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1

        if tag == "html":
            self.html_attrs = attrs
        elif tag == "body":
            self._in_body = True
        elif tag == "meta":
            self.metas.append(attrs)
        elif tag == "nav":
            self.navs.append(attrs)
        elif tag == "link":
            rel = normalize_text(attrs.get("rel", "")).lower()
            if "stylesheet" in rel:
                self.stylesheet_links.append(attrs)
        elif tag == "title":
            self._in_title = True
        elif tag in {"h1", "h2"}:
            self._heading_stack.append({"tag": tag, "parts": []})
        elif tag == "a":
            self.links.append({"attrs": attrs, "text_parts": []})
            self._active_link_indices.append(len(self.links) - 1)

    def handle_data(self, data):
        if self._in_body:
            self.body_text_parts.append(data)
        if self._in_title:
            self.title_parts.append(data)
        for index in self._active_link_indices:
            self.links[index]["text_parts"].append(data)
        if self._heading_stack:
            self._heading_stack[-1]["parts"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "body":
            self._in_body = False
        elif tag == "a" and self._active_link_indices:
            self._active_link_indices.pop()
        elif tag in {"h1", "h2"} and self._heading_stack:
            heading = self._heading_stack.pop()
            if heading["tag"] == tag:
                self.headings.append(
                    {
                        "tag": tag,
                        "text": normalize_text("".join(heading["parts"])),
                    }
                )

    @property
    def title(self):
        return normalize_text("".join(self.title_parts))

    @property
    def text(self):
        return normalize_text(" ".join(self.body_text_parts))

    def heading_texts(self, tag):
        return [heading["text"] for heading in self.headings if heading["tag"] == tag]

    def link_hrefs(self):
        return [link["attrs"].get("href", "") for link in self.links]

    def link_texts_by_href(self):
        return {
            link["attrs"].get("href", ""): normalize_text("".join(link["text_parts"]))
            for link in self.links
        }


def parse_page(page_key):
    path = REPO_ROOT / PAGES[page_key]
    parser = StaticPageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


class StaticSiteContractTests(unittest.TestCase):
    def test_public_pages_exist_with_expected_html_metadata(self):
        for page_key, relative_path in PAGES.items():
            with self.subTest(page=page_key):
                path = REPO_ROOT / relative_path
                self.assertTrue(path.is_file())

                page = parse_page(page_key)
                self.assertIn("doctype html", [decl.lower() for decl in page.declarations])
                self.assertEqual(page.html_attrs.get("lang"), "en")
                self.assertEqual(page.title, EXPECTED_TITLES[page_key])
                self.assertEqual(page.heading_texts("h1"), [EXPECTED_H1S[page_key]])

                charset_metas = [
                    meta for meta in page.metas if meta.get("charset", "").lower() == "utf-8"
                ]
                self.assertEqual(len(charset_metas), 1)

                viewport_metas = [
                    meta for meta in page.metas if meta.get("name", "").lower() == "viewport"
                ]
                self.assertEqual(len(viewport_metas), 1)
                viewport_content = viewport_metas[0].get("content", "")
                self.assertIn("width=device-width", viewport_content)
                self.assertIn("initial-scale=1", viewport_content)

    def test_pages_do_not_include_client_runtime_or_remote_styles(self):
        blocked_tags = {"script", "iframe", "form"}

        for page_key in PAGES:
            with self.subTest(page=page_key):
                page = parse_page(page_key)
                for tag in blocked_tags:
                    self.assertEqual(page.tag_counts.get(tag, 0), 0)
                self.assertEqual(page.stylesheet_links, [])
                self.assertGreaterEqual(page.tag_counts.get("style", 0), 1)

    def test_all_links_are_resolvable_or_approved_https_destinations(self):
        for page_key, relative_path in PAGES.items():
            page = parse_page(page_key)
            source_path = REPO_ROOT / relative_path

            for href in page.link_hrefs():
                with self.subTest(page=page_key, href=href):
                    self.assertTrue(href)
                    parsed = urlparse(href)

                    if parsed.scheme:
                        self.assertEqual(parsed.scheme, "https")
                        self.assertIn(parsed.netloc, APPROVED_EXTERNAL_HOSTS)
                        continue

                    if href.startswith("#"):
                        continue

                    target_path = (source_path.parent / parsed.path).resolve()
                    if parsed.path.endswith("/") or target_path.is_dir():
                        target_path = target_path / "index.html"

                    self.assertTrue(
                        target_path.is_file(),
                        f"{href} from {relative_path} should resolve to an existing file",
                    )
                    self.assertTrue(
                        target_path.is_relative_to(REPO_ROOT),
                        f"{href} from {relative_path} should stay inside this site",
                    )

    def test_home_page_links_to_primary_public_routes(self):
        page = parse_page("home")
        link_texts = page.link_texts_by_href()

        self.assertEqual(set(link_texts), {"./privacy/", "./support/"})
        self.assertIn("Privacy Policy", link_texts["./privacy/"])
        self.assertIn("How Atlas handles workout data", link_texts["./privacy/"])
        self.assertIn("Support", link_texts["./support/"])
        self.assertIn("Get help with Atlas", link_texts["./support/"])

        self.assertEqual(len(page.navs), 1)
        self.assertEqual(page.navs[0].get("aria-label"), "Atlas pages")

    def test_secondary_pages_link_back_to_home(self):
        for page_key in ("privacy", "support"):
            with self.subTest(page=page_key):
                page = parse_page(page_key)
                link_texts = page.link_texts_by_href()
                self.assertIn("../", link_texts)
                self.assertEqual(link_texts["../"], "Atlas")


class PrivacyPolicyContentTests(unittest.TestCase):
    def test_privacy_policy_sections_are_complete_and_ordered(self):
        page = parse_page("privacy")

        self.assertEqual(
            page.heading_texts("h2"),
            [
                "Summary",
                "Data Stored On Your Device",
                "Bluetooth Heart-Rate Sensors",
                "Apple Health",
                "Export And Restore",
                "Data Collection",
                "Tracking, Advertising, And Analytics",
                "Data Sharing",
                "Children",
                "Medical Disclaimer",
                "Changes To This Policy",
                "Contact",
            ],
        )

    def test_privacy_policy_has_parseable_effective_date(self):
        page = parse_page("privacy")
        marker = "Effective date: "
        self.assertIn(marker, page.text)
        date_text = page.text.split(marker, 1)[1].split(" Atlas is an iPhone", 1)[0]
        self.assertEqual(datetime.strptime(date_text, "%B %d, %Y").date().isoformat(), "2026-05-19")

    def test_privacy_policy_preserves_current_data_handling_claims(self):
        page = parse_page("privacy")
        text = page.text.lower()

        required_claims = [
            "does not require an account",
            "does not use ads",
            "does not use analytics sdks",
            "does not track you across apps or websites",
            "does not send your workout data to a developer-operated server",
            "locally on your device",
            "bluetooth sensor use is optional",
            "does not use healthkit",
            "does not request access to apple health",
            "does not operate a backend service",
            "does not transmit your workout data",
            "does not sell your data",
            "does not share your data with advertisers",
            "not a medical device",
        ]

        for claim in required_claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, text)

    def test_privacy_policy_names_the_local_data_categories(self):
        page = parse_page("privacy")
        text = page.text.lower()

        expected_categories = [
            "workout sessions",
            "exercises",
            "sets",
            "weights",
            "reps",
            "workout notes",
            "training preferences",
            "body weight",
            "muscle-volume targets",
            "heart-rate samples",
            "export and restore preferences",
            "folder bookmark",
        ]

        for category in expected_categories:
            with self.subTest(category=category):
                self.assertIn(category, text)

    def test_privacy_policy_contact_points_to_support_page(self):
        page = parse_page("privacy")
        link_texts = page.link_texts_by_href()

        self.assertIn("../support/", link_texts)
        self.assertIn("atlas-support/support/", link_texts["../support/"])


class SupportContentTests(unittest.TestCase):
    def test_support_page_sections_are_complete_and_ordered(self):
        page = parse_page("support")

        self.assertEqual(
            page.heading_texts("h2"),
            [
                "Get Help",
                "Common Notes",
                "Privacy Policy",
            ],
        )

    def test_support_page_points_to_public_issue_tracker_and_privacy_page(self):
        page = parse_page("support")
        link_texts = page.link_texts_by_href()

        issue_url = "https://github.com/austinlansing12-blip/atlas-support/issues"
        self.assertIn(issue_url, link_texts)
        self.assertEqual(link_texts[issue_url], issue_url)

        self.assertIn("../privacy/", link_texts)
        self.assertIn("atlas-support/privacy/", link_texts["../privacy/"])

    def test_support_page_warns_against_posting_sensitive_details(self):
        page = parse_page("support")
        text = page.text.lower()

        self.assertIn("avoid including private workout, health, or personal details", text)
        self.assertIn("does not require an account or login", text)
        self.assertIn("workout data is stored locally on your device", text)
        self.assertIn("bluetooth heart-rate sensor support is optional", text)
        self.assertIn("not a medical device", text)


if __name__ == "__main__":
    unittest.main()
