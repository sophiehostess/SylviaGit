__author__ = 'miaozhuzhu'


import unittest

import datetime

import Rate2 as Rate


if __name__ == '__main__':
    unittest.main()


class Test_cls_currency(unittest.TestCase):

    def test_init(self):
        USD = Rate.cls_currency("USD", 1000, 360)
        self.assertEqual(USD.label, "USD")
        self.assertEqual(USD.factor, 1000)
        self.assertEqual(USD.number_of_days_1year, 360)
        self.assertTrue(isinstance(USD, Rate.cls_currency))


class Test_cls_currency_pair(unittest.TestCase):

    def test_init(self):
        EUR= Rate.cls_currency("EUR")
        USD = Rate.cls_currency("USD")
        EURUSD = Rate.cls_currency_pair(EUR,USD, Rate.quotation_mode_enum.base_und,1000 , 365 ,2)
        self.assertEqual(EURUSD.quotation, "EUR-USD")
        self.assertEqual(EURUSD.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(EURUSD.swap_point_factor, 1000)
        self.assertEqual(EURUSD.day_shift, 2)
        self.assertEqual(EURUSD.number_of_days_1year, 365)
<<<<<<< HEAD
        self.assertTrue(isinstance(EURUSD + “” + “”, Rate.cls_currency_pair))
=======
        self.assertTrue(isinstance(EURUSD + “”, Rate.cls_currency_pair))
>>>>>>> feature1
