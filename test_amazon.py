"""Test del parser Amazon.it: deve reggere formati numerici IT e USA e piu' termini."""
import unittest

from product_gap.adapters.amazon import conta_da_incolla, estrai_conteggi


class TestAmazonParser(unittest.TestCase):
    def test_formato_italiano_migliaia(self):
        # 1.234 = milleduecento... -> > 1000
        self.assertEqual(conta_da_incolla("Ottimo prodotto 1.234 recensioni"), 1)

    def test_formato_usa_migliaia(self):
        # 1,234 reviews (formato USA) prima veniva letto come 1.234 -> ora corretto
        self.assertEqual(conta_da_incolla("Great item 1,234 reviews"), 1)

    def test_sotto_soglia_non_conta(self):
        self.assertEqual(conta_da_incolla("Nuovo 987 recensioni"), 0)

    def test_termini_vari(self):
        testo = "12,345 ratings\n2.500 valutazioni\n1.500 voti\n800 reviews"
        self.assertEqual(conta_da_incolla(testo), 3)  # 800 sotto soglia

    def test_elenco_misto(self):
        testo = (
            "Prodotto A - 4,6 su 5 stelle - 15.230 recensioni\n"
            "Prodotto B - 4,2 su 5 stelle - 340 recensioni\n"
            "Prodotto C - 4,8 su 5 stelle - 3,102 reviews\n"
        )
        self.assertEqual(estrai_conteggi(testo), [15230, 340, 3102])
        self.assertEqual(conta_da_incolla(testo), 2)

    def test_vuoto(self):
        self.assertEqual(conta_da_incolla(""), 0)
        self.assertEqual(conta_da_incolla(None), 0)


if __name__ == "__main__":
    unittest.main()
