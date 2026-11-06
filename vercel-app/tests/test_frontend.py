"""Regression checks: frontend must render even if Vercel static asset routes fail."""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import home, get_dashboard


class FrontendSmokeTests(unittest.TestCase):
    def test_home_includes_styles_scripts_and_data(self):
        response = home()
        self.assertEqual(response.status_code, 200)
        html = response.body.decode("utf-8")
        self.assertIn('<style id="dashboard-style">', html)
        self.assertIn('<script id="dashboard-script">', html)
        self.assertIn('<script id="dashboard-bootstrap" type="application/json">', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn(".metric-grid", (Path(__file__).resolve().parents[1] / "public" / "app.css").read_text())
        self.assertIn('const bundledData = embedded', html)
        self.assertNotIn('<link rel="stylesheet" href="/assets/app.css">', html)
        self.assertNotIn('<script src="/assets/app.js" defer></script>', html)

        match = re.search(
            r'<script id="dashboard-bootstrap" type="application/json">(.*?)</script>',
            html, re.S,
        )
        self.assertIsNotNone(match)
        all_periods = json.loads(match.group(1))
        self.assertEqual(set(all_periods), {"30d", "90d", "180d", "365d"})
        for period, data in all_periods.items():
            self.assertEqual(data["meta"]["period"], period)
            self.assertGreater(data["kpis"]["orders"], 0)

    def test_api_remains_available(self):
        response = get_dashboard("90d")
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload["meta"]["period"], "90d")
        self.assertEqual(payload["meta"]["mode"], "demo")


if __name__ == "__main__":
    unittest.main()
