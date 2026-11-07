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
        self.assertEqual(response.headers.get("x-dashboard-render"), "fastapi-inline-v8")
        root = Path(__file__).resolve().parents[1]
        self.assertFalse((root / "public" / "index.html").exists(),
                         "Public index.html would shadow the FastAPI homepage on Vercel")
        self.assertTrue((root / "templates" / "index.html").exists())
        html = response.body.decode("utf-8")
        self.assertIn('<style id="dashboard-style">', html)
        self.assertIn('id="dashboard-script"', html)
        self.assertIn('<style id="dashboard-upgrade-style">', html)
        self.assertIn('id="dashboard-upgrade-script"', html)
        self.assertIn('<style id="dashboard-studio-style">', html)
        self.assertIn('id="dashboard-studio-script"', html)
        self.assertIn('<style id="dashboard-integrations-style">', html)
        self.assertIn('id="dashboard-integrations-script"', html)
        self.assertIn('<style id="dashboard-responsive-style">', html)
        self.assertIn('id="dashboard-responsive-script"', html)
        self.assertIn('bottom.id = "mobileBottomNav"', html)
        self.assertIn('mobile-sidebar-close', html)
        self.assertIn('viewport-fit=cover', html)
        self.assertIn("integrationDbForm", html)
        self.assertIn("syncDatabase", html)
        self.assertIn("data-sync-auto", html)
        self.assertIn("integrationFileForm", html)
        self.assertIn("integrationsNav", html)
        self.assertIn("INTEGRATION_ALLOWED_HOSTS", html)
        self.assertIn('v3CommandButton', html)
        self.assertIn('v3CompareButton', html)
        self.assertIn('v3-chartswitch', html)
        self.assertIn('enterprise:rendered', html)
        self.assertIn('id="v2Module"', html)
        self.assertIn('data-v2-tab', html)
        self.assertIn('data-scenario', html)
        self.assertIn('/api/powerbi/kit', html)
        self.assertIn('id="dashboard-bootstrap" type="application/json"', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn(".metric-grid", (Path(__file__).resolve().parents[1] / "templates" / "app.css").read_text())
        self.assertIn('const bundledData = embedded', html)
        self.assertIn('id="assistantPanel"', html)
        self.assertIn('id="aiSettingsOverlay"', html)
        self.assertIn('id="granularitySelect"', html)
        self.assertIn('id="assistantLauncher"', html)
        self.assertIn('const ai = {provider:', html)
        self.assertNotIn('<link rel="stylesheet" href="/assets/app.css">', html)
        self.assertNotIn('<script src="/assets/app.js" defer></script>', html)

        match = re.search(
            r'<script nonce="[^"]+" id="dashboard-bootstrap" type="application/json">(.*?)</script>',
            html, re.S,
        )
        self.assertIsNotNone(match)
        all_periods = json.loads(match.group(1))
        self.assertEqual(set(all_periods), {"30d", "90d", "180d", "365d"})
        for period, data in all_periods.items():
            self.assertEqual(data["meta"]["period"], period)
            self.assertGreater(data["kpis"]["orders"], 0)
            self.assertTrue(data["smart"]["insights"])

    def test_api_remains_available(self):
        response = get_dashboard("90d")
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload["meta"]["period"], "90d")
        self.assertEqual(payload["meta"]["mode"], "demo")


if __name__ == "__main__":
    unittest.main()
