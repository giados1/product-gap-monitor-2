"""Test automatici del motore di scoring e degli alert (nessuna chiamata di rete)."""
import unittest

from product_gap.analytics import delta_alert
from product_gap.scoring import load_config, score_snapshot

cfg = load_config()


def base():
    return {
        "trend_it_volume": 10.0,
        "trend_global_volume": 80.0,
        "trend_ratio": 8.0,
        "trend_it_direction": "in_salita",
        "tiktok_it": "presente",
        "meta_advertisers_it": 0,
        "amazon_sellers_over_1000": 1,
    }


class TestScoring(unittest.TestCase):
    def test_gap_aperto(self):
        res = score_snapshot(cfg, base())
        self.assertEqual(res["verdict"], "GAP_APERTO")
        self.assertGreaterEqual(res["score"], 80)

    def test_presidiato_meta_ads(self):
        d = base()
        d["meta_advertisers_it"] = 3  # sopra la soglia 0
        res = score_snapshot(cfg, d)
        self.assertEqual(res["verdict"], "MERCATO_PRESIDIATO")
        self.assertLess(res["score"], 80)

    def test_presidiato_amazon(self):
        d = base()
        d["amazon_sellers_over_1000"] = 12  # sopra la soglia 6
        res = score_snapshot(cfg, d)
        self.assertEqual(res["verdict"], "MERCATO_PRESIDIATO")

    def test_ratio_sotto_minimo(self):
        d = base()
        d["trend_it_volume"], d["trend_global_volume"], d["trend_ratio"] = 40.0, 60.0, 1.5
        res = score_snapshot(cfg, d)
        self.assertEqual(res["verdict"], "MERCATO_PRESIDIATO")

    def test_dati_insufficienti(self):
        d = {k: None for k in base()}
        d["trend_it_volume"], d["trend_global_volume"] = 10.0, 80.0
        d["trend_ratio"], d["trend_it_direction"] = 8.0, "in_salita"
        res = score_snapshot(cfg, d)
        self.assertEqual(res["verdict"], "DATI_INSUFFICIENTI")

    def test_delta_alert_meta_in_crescita(self):
        prec = base()
        ult = dict(base())
        ult["meta_advertisers_it"] = 2
        alerts = delta_alert(cfg, prec, ult)
        self.assertTrue(any("Meta" in a for a in alerts))

    def test_delta_alert_ratio_sceso(self):
        prec = base()
        ult = dict(base())
        ult["trend_ratio"], ult["trend_it_volume"], ult["trend_global_volume"] = 4.0, 25.0, 100.0
        alerts = delta_alert(cfg, prec, ult)
        self.assertTrue(any("atterrato" in a for a in alerts))


if __name__ == "__main__":
    unittest.main()
