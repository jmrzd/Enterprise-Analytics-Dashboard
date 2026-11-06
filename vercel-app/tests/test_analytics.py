"""Unit tests for the public, dependency-free synthetic analytics engine."""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 6)
        self.data = dashboard("90d", self.today)

    def test_consistency_of_sales(self):
        d = self.data
        self.assertGreaterEqual(d["kpis"]["revenue"], sum(x["revenue"] for x in d["products"]))
        self.assertEqual(d["kpis"]["revenue"], sum(x["value"] for x in d["categories"]))
        self.assertEqual(d["kpis"]["orders"], d["statuses"][0]["value"])

    def test_finance_is_separate_and_balanced(self):
        k = self.data["kpis"]
        self.assertAlmostEqual(k["income"] - k["expenses"], k["cashBalance"], places=2)
        self.assertEqual(k["headcount"], sum(d["headcount"] for d in self.data["departments"]))

    def test_period_filter_and_determinism(self):
        short = dashboard("30d", self.today)
        full = dashboard("365d", self.today)
        self.assertLess(short["kpis"]["orders"], full["kpis"]["orders"])
        self.assertEqual(self.data, dashboard("90d", self.today))
        self.assertEqual(short["meta"]["mode"], "demo")

    def test_invalid_period(self):
        with self.assertRaises(ValueError):
            dashboard("secret", self.today)

    def test_no_private_data(self):
        self.assertNotIn("DATABASE_URL", str(self.data))
        self.assertIn("sintéticos", self.data["meta"]["disclaimer"])


if __name__ == "__main__":
    unittest.main()
