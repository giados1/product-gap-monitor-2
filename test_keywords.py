"""Test del suggeritore di keyword dal nome prodotto."""
import unittest

from product_gap.keywords import suggerisci_keyword


class TestKeywords(unittest.TestCase):
    def test_preferisce_parentesi_inglese(self):
        self.assertEqual(
            suggerisci_keyword("Bigodini senza calore (heatless curls)"), "heatless curls"
        )

    def test_nome_italiano_pulito(self):
        self.assertEqual(
            suggerisci_keyword("Coperta sauna a infrarossi"), "coperta sauna infrarossi"
        )

    def test_toglie_punteggiatura(self):
        self.assertEqual(suggerisci_keyword("Lampada LED da scrivania!!!"), "lampada led scrivania")

    def test_vuoto(self):
        self.assertEqual(suggerisci_keyword(""), "")
        self.assertEqual(suggerisci_keyword(None), "")


if __name__ == "__main__":
    unittest.main()
