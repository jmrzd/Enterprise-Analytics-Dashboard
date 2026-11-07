"""Business features: insights, what-if scenarios and genuine Power BI exports."""
import csv
import io
import json
import sys
import unittest
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analytics import dashboard
from features import ScenarioInput, calculate_scenario, insights_for, export_data, create_powerbi_kit
from app import insights, scenario, powerbi_export, powerbi_kit, powerbi_dax


class FeaturesTests(unittest.TestCase):
    def setUp(self):
        self.dataset=dashboard("90d",date(2026,11,6))

    def test_insights_are_mathematically_explainable(self):
        data=insights_for(self.dataset)
        self.assertGreaterEqual(len(data["insights"]),3)
        self.assertTrue(all(x["title"] and x["view"] for x in data["insights"]))
        category=max(self.dataset["categories"],key=lambda x:x["value"])
        actual=category["value"]/self.dataset["kpis"]["revenue"]*100
        self.assertAlmostEqual(data["summary"]["categoryShare"],actual,places=1)
        self.assertTrue(data["alerts"])
        self.assertIn("sintéticos",data["note"])

    def test_scenario_zero_input_equals_baseline(self):
        result=calculate_scenario(ScenarioInput(),self.dataset)
        self.assertEqual(result["baseline"]["revenue"],result["scenario"]["revenue"])
        self.assertEqual(result["baseline"]["grossProfit"],result["scenario"]["grossProfit"])
        self.assertEqual(result["delta"]["grossProfit"],0.0)
        self.assertEqual(result["scenario"]["extraMonthlyPayroll"],0.0)

    def test_scenario_formulas(self):
        opts=ScenarioInput(price_pct=10,volume_pct=20,cost_pct=-5,hires=2,expense_reduction_pct=15)
        result=calculate_scenario(opts,self.dataset)
        k=self.dataset["kpis"]
        expected_revenue=k["revenue"]*1.1*1.2
        expected_cogs=(k["revenue"]-k["grossProfit"])*1.2*.95
        self.assertAlmostEqual(result["scenario"]["revenue"],round(expected_revenue,2),places=2)
        self.assertAlmostEqual(result["scenario"]["grossProfit"],round(expected_revenue-expected_cogs,2),places=2)
        self.assertAlmostEqual(result["scenario"]["expenseSavings"],round(k["expenses"]*.15,2),places=2)
        self.assertEqual(result["scenario"]["headcount"],k["headcount"]+2)
        self.assertIn("não representa",result["disclaimer"])

    def test_export_revenue_equals_monthly_data(self):
        contents=export_data("vendas",self.dataset).decode("utf-8-sig")
        reader=csv.DictReader(io.StringIO(contents),delimiter=";")
        rows=list(reader)
        self.assertEqual(len(rows),len(self.dataset["months"]))
        self.assertEqual(reader.fieldnames,["mes_inicio","mes","receita","lucro_bruto","pedidos_concluidos"])
        self.assertTrue(all(r["mes_inicio"].endswith("-01") for r in rows))
        self.assertAlmostEqual(sum(float(r["receita"]) for r in rows),self.dataset["kpis"]["revenue"],places=2)

    def test_every_powerbi_file_can_be_downloaded(self):
        files=("vendas","financeiro","rh","produtos","clientes","categorias")
        for name in files:
            with self.subTest(name=name):
                data=export_data(name,self.dataset)
                self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
                self.assertGreater(len(data),70)
        buffer=io.BytesIO(create_powerbi_kit(self.dataset))
        with zipfile.ZipFile(buffer) as z:
            self.assertEqual(set(z.namelist()),{*(name+".csv" for name in files),"medidas.dax","LEIA-ME.txt"})
            self.assertIn("FatoVendas",z.read("medidas.dax").decode("utf-8"))
            self.assertIn("sintéticos",z.read("LEIA-ME.txt").decode("utf-8"))

    def test_fastapi_endpoints(self):
        response=insights("90d")
        self.assertEqual(response.status_code,200)
        self.assertTrue(json.loads(response.body)["insights"])
        simulated=scenario(ScenarioInput(period="30d",price_pct=5))
        self.assertEqual(simulated.status_code,200)
        self.assertGreater(json.loads(simulated.body)["delta"]["revenue"],0)
        exported=powerbi_export("rh","90d")
        self.assertEqual(exported.status_code,200)
        self.assertIn("attachment",exported.headers["content-disposition"])
        zip_response=powerbi_kit("90d")
        self.assertEqual(zip_response.status_code,200)
        self.assertEqual(zip_response.media_type,"application/zip")
        self.assertIn("Margem Bruta",powerbi_dax().body.decode("utf-8"))


if __name__=="__main__":
    unittest.main()
