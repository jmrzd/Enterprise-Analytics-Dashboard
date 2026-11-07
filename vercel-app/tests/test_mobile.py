"""Regression checks for viewport-safe, touch-friendly, accessible frontend."""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import home

ROOT = Path(__file__).resolve().parents[1]


class MobileLayoutTests(unittest.TestCase):
    def setUp(self):
        self.html = home().body.decode("utf-8")
        self.css = (ROOT / "templates" / "responsive.css").read_text(encoding="utf-8")
        self.js = (ROOT / "templates" / "responsive.js").read_text(encoding="utf-8")

    def test_iphone_viewport_and_safe_area(self):
        self.assertIn('viewport-fit=cover', self.html)
        self.assertIn('apple-mobile-web-app-capable', self.html)
        self.assertIn('env(safe-area-inset-bottom', self.css)
        self.assertIn('env(safe-area-inset-top', self.css)
        self.assertIn('100dvh', self.css)
        self.assertIn('100svh', self.css)
        self.assertIn('-webkit-overflow-scrolling: touch', self.css)
        self.assertIn('-webkit-backdrop-filter', self.css)
        self.assertIn('font-size: 16px !important', self.css)

    def test_embedded_responsive_assets_are_last_and_nonce_protected(self):
        self.assertIn('<style id="dashboard-responsive-style">', self.html)
        self.assertIn('id="dashboard-responsive-script"', self.html)
        self.assertIn('id="dashboard-integrations-script"', self.html)
        self.assertLess(
            self.html.index('id="dashboard-integrations-script"'),
            self.html.index('id="dashboard-responsive-style"')
        )
        self.assertLess(
            self.html.index('id="dashboard-responsive-style"'),
            self.html.index('id="dashboard-responsive-script"')
        )
        for match in re.finditer(r"<script\b([^>]*)>", self.html):
            self.assertIn('nonce="', match.group(1), "All inline scripts need CSP nonce")
        self.assertIn('window.matchMedia("(max-width: 960px)")', self.js)

    def test_mobile_navigation_and_touch_chart_inspector(self):
        self.assertIn('id = "mobileBottomNav"', self.js)
        self.assertIn('data-mobile-id=', self.js)
        self.assertIn('data-tip', self.js)
        self.assertIn('ea-menu-locked', self.js)
        self.assertIn('appShell.insertBefore(overlay, appShell.firstChild)', self.js)
        self.assertIn('mobile-sidebar-close', self.js)
        self.assertIn('visualViewport', self.js)
        self.assertIn('className = "ea-mobile-svg-scroll"', self.js)
        self.assertIn('aria-label', self.js)
        self.assertIn('overflow-x: auto', self.css)
        self.assertIn('.v2-tabs', self.css)
        self.assertIn('.v3-graph .chart-area', self.css)

    def test_no_mobile_secret_storage_in_new_js(self):
        self.assertNotIn("localStorage", self.js)
        self.assertNotIn("sessionStorage", self.js)
        self.assertNotIn("api_key", self.js)
        self.assertNotIn("admin_token", self.js)


if __name__ == "__main__":
    unittest.main()
