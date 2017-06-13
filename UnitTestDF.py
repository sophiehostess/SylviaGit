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
        EURUSD = Rate.cls_currency_pair(EUR,USD, Rate.quotation_mode_enum.base_und,1000, 365,2)
        self.assertEqual(EURUSD.quotation, "EUR-USD")
        self.assertEqual(EURUSD.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(EURUSD.swap_point_factor, 1000)
        self.assertEqual(EURUSD.day_shift, 2)
        self.assertEqual(EURUSD.number_of_days_1year, 365)
        self.assertTrue(isinstance(EURUSD, Rate.cls_currency_pair))

        USDEUR = EURUSD.get_reversed_pair()
        self.assertEqual(USDEUR.quotation, "USD-EUR")
        self.assertEqual(USDEUR.quotation_mode, Rate.quotation_mode_enum.und_base)
        self.assertEqual(USDEUR.get_reversed_quotation_mode(), Rate.quotation_mode_enum.base_und)


class Test_cls_tenor(unittest.TestCase):

    def test_init(self):
        one_month=Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17), "1M")
        self.assertEqual(one_month.start_date, datetime.date(2016,12,17))
        self.assertEqual(one_month.maturity_date, datetime.date(2017,1,17))
        self.assertEqual(one_month.number_of_days, 31)

        one_month_inverse = one_month.get_inverse_tenor()
        self.assertEqual(one_month_inverse.start_date, datetime.date(2017,1,17))
        self.assertEqual(one_month_inverse.maturity_date, datetime.date(2016,12,17))
        self.assertEqual(one_month_inverse.number_of_days, -31)
        self.assertEqual(one_month_inverse.label, "1M inverse".upper())


class Test_cls_rate(unittest.TestCase):

    def test_init(self):
        one_month=Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17), "1M")
        RATE1= Rate.cls_rate(one_month,6.0,6.2,5.8)
        self.assertEqual(RATE1.mid,6.0)
        self.assertEqual(RATE1.bid,6.2)
        self.assertEqual(RATE1.ask,5.8)
        self.assertEqual(round(RATE1.spread,5),0.2)

        RATE2= Rate.cls_rate(one_month)
        RATE2.set_rate_by_mid_spread(1.2,0.3)
        self.assertEqual(RATE2.mid,1.2)
        self.assertEqual(round(RATE2.bid,5),0.9)
        self.assertEqual(round(RATE2.ask,5),1.5)
        self.assertEqual(round(RATE2.spread,5),0.3)

        RATE3= Rate.cls_rate(one_month)
        RATE3.set_rate_by_bid_ask(1200,1500)
        self.assertEqual(RATE3.mid,1350)
        self.assertEqual(round(RATE3.bid,5),1200)
        self.assertEqual(round(RATE3.ask,5),1500)
        self.assertEqual(round(RATE3.spread,5),150)



class Test_cls_single_currency_rate(unittest.TestCase):
    def test_init(self):
        EUR= Rate.cls_currency("EUR")
        one_month=Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17), "1M")
        RATE1 = Rate.cls_single_currency_rate(EUR,one_month,1.3)
        self.assertEqual(RATE1.mid,1.3)
        self.assertEqual(RATE1.bid,1.3)
        self.assertEqual(RATE1.ask,1.3)
        self.assertEqual(RATE1.tenor.maturity_date,datetime.date(2017,1,17))



class Test_cls_discount_factor(unittest.TestCase):
    def test_init(self):
        EUR= Rate.cls_currency("EUR")
        one_month=Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17), "1M")
        DF1 = Rate.cls_discount_factor(EUR,one_month,0.997)
        CF1 = DF1.get_capitalized_factor()
        self.assertEqual(DF1.mid,1/CF1.mid)
        DR1 = DF1.get_discount_rate()
        self.assertEqual(1/(DR1.mid * (datetime.date(2017,1,17) - datetime.date(2016,12,17)).days / 365 + 1), DF1.mid)

class Test_cls_discount_factor_curve(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 1000, 360)

        df_1d = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2016,12,18),"O/N"),0.79)
        df_2d = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2016,12,19),"T/N"),0.89)
        df_1m = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17),"1M"),0.90001)
        df_1y = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,12,17),"1Y"),0.91000)

        usd_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_2d,df_1d,df_1y,df_1m], Rate.linearization_enum.linear_ds_rate)

        df1 = usd_df_curve.get_discount_factor_by_maturity_date(datetime.date(2017,6,20))
        print(df1.mid)

        usd_cf_curve = Rate.cls_capitalized_factor_curve(usd_ccy,[df_2d.get_capitalized_factor(),df_1d.get_capitalized_factor(),df_1y.get_capitalized_factor(),df_1m.get_capitalized_factor()], Rate.linearization_enum.linear_ds_rate)

        cf1 = usd_cf_curve.get_capitalized_factor_by_maturity_date(datetime.date(2017,6,20))
        print(1/cf1.mid)

        self.assertEqual(df1.mid,1/cf1.mid)