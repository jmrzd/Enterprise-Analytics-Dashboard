"""Verifies accurate prior-window comparisons and the new standalone UI assets."""
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import _events, dashboard, PERIOD_DAYS

ROOT = Path(__file__).resolve().parents[1]


class StudioTests(unittest.TestCase):
    def test_prior_window_uses_exact_days_for_every_supported_period(self):
        today = date(2026, 11, 7)
        sales, _, cash = _events(today)
        for period in ("30d", "90d", "180d"):
            with self.subTest(period=period):
                days = PERIOD_DAYS[period]
                current_start = today - timedelta(days=days - 1)
                previous_start = current_start - timedelta(days=days)
                previous_end = current_start - timedelta(days=1)
                result = dashboard(period, today)
                previous = result["comparison"]
                self.assertEqual(previous["from"], previous_start.isoformat())
                self.assertEqual(previous["to"], previous_end.isoformat())
                prev_sales = [item for item in sales
                              if previous_start <= item["date"] < current_start]
                prev_cash = [item for item in cash
                             if previous_start <= item["date"] < current_start]
                expected_income = sum(c["amount"] for c in prev_cash if c["kind"] == "receita")
                expected_expenses = sum(c["amount"] for c in prev_cash if c["kind"] == "despesa")
                self.assertEqual(previous["orders"], len(prev_sales))
                self.assertEqual(previous["revenue"], sum(s["revenue"] for s in prev_sales))
                self.assertEqual(previous["grossProfit"], sum(s["profit"] for s in prev_sales))
                self.assertAlmostEqual(previous["cashBalance"],
                                       round(expected_income - expected_expenses, 2), places=2)

    def test_year_comparison_not_misrepresented(self):
        self.assertIsNone(dashboard("365d", date(2026, 11, 7))["comparison"])

    def test_command_center_and_chart_assets_exist(self):
        css = (ROOT / "templates" / "studio.css").read_text(encoding="utf-8")
        js = (ROOT / "templates" / "studio.js").read_text(encoding="utf-8")
        self.assertIn(".v3-chartswitch", css)
        self.assertIn(".v2-tabs", css)
        self.assertIn('data-v3-mode', js)
        self.assertIn('data-v3-series', js)
        self.assertIn('v3CompareButton', js)
        self.assertIn('v3CommandInput', js)
        self.assertIn('enterprise:rendered', js)
        self.assertIn('function renderNotifications()', js)
        self.assertIn('function makeSmooth(points)', js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("sessionStorage", js)


if __name__ == "__main__":
    unittest.main()
