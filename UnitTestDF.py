#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime

import Rate2 as Rate


if __name__ == '__main__':
    unittest.main()


class Test_cls_currency(unittest.TestCase):

    def test_init(self):
        USD = Rate.cls_currency("USD", 360)
        self.assertEqual(USD.label, "USD")
        self.assertEqual(USD.number_of_days_1year, 360)
        self.assertTrue(isinstance(USD, Rate.cls_currency))


class Test_cls_currency_pair(unittest.TestCase):

    def test_init(self):
        EUR= Rate.cls_currency("EUR")
        USD = Rate.cls_currency("USD")
        EURUSD = Rate.cls_currency_pair(EUR,USD, Rate.quotation_mode_enum.base_und,1000, 2)
        self.assertEqual(EURUSD.quotation, "EUR-USD")
        self.assertEqual(EURUSD.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(EURUSD.swap_point_factor, 1000)
        self.assertEqual(EURUSD.day_shift, 2)
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


# class Test_cls_discount_factor_curve_linear_ds_rate(unittest.TestCase):
#     def test_init(self):
#         usd_ccy = Rate.cls_currency("USD", 1000, 360)
#
#         df_1d = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2016,12,18),"O/N"),0.79)
#         df_2d = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2016,12,19),"T/N"),0.89)
#         df_1m = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17),"1M"),0.90001)
#         df_1y = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,12,17),"1Y"),0.91000)
#
#         usd_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_2d,df_1d,df_1y,df_1m], Rate.linearization_enum.linear_ds_rate)
#
#         df1 = usd_df_curve.get_discount_factor_by_maturity_date(datetime.date(2017,6,20))
#         print(df1.mid)
#
#         usd_cf_curve = Rate.cls_capitalized_factor_curve(usd_ccy,[df_2d.get_capitalized_factor(),df_1d.get_capitalized_factor(),df_1y.get_capitalized_factor(),df_1m.get_capitalized_factor()], Rate.linearization_enum.linear_ds_rate)
#
#         cf1 = usd_cf_curve.get_capitalized_factor_by_maturity_date(datetime.date(2017,6,20))
#         print(1/cf1.mid)
#
#         self.assertEqual(df1.mid,1/cf1.mid)



class Test_cls_capitalized_factor(unittest.TestCase):
    def test_init(self):
        EUR = Rate.cls_currency("EUR")
        one_month = Rate.cls_tenor(datetime.date(2016, 12, 17), datetime.date(2017, 1, 17), "1M")
        CF1 = Rate.cls_capitalized_factor(EUR, one_month, 1/0.997)
        DF1 = CF1.get_discount_factor()
        self.assertEqual(1 / DF1.mid, CF1.mid)
        DR1 = CF1.get_discount_rate()
        self.assertEqual((DR1.mid * (datetime.date(2017, 1, 17) - datetime.date(2016, 12, 17)).days / 365 + 1), CF1.mid)



class Test_cls_discount_factor_curve_log_ds_factor(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360)

        df_ON = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,6,14),"O/N"),0.999968868900009)
        df_TN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,6,15),"T/N"),0.999937738800022)
        df_SN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,6,16),"S/N"),0.999907939100022)
        df_1W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,6,22),"1W"),0.999727254200085)
        df_2W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,6,29),"2W"),0.999512368799956)
        df_1M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,7,17),"1M"),0.998942551320812)
        df_2M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,8,15),"2M"),0.997910475099995)
        df_3M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,9,15),"3M"),0.996788096599609)
        df_6M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2017,12,15),"6M"),0.993355657098983)
        df_9M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2018,3,15),"9M"),0.989821542597184)
        df_1Y = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(datetime.date(2017, 6,13),datetime.date(2018,6,17),"1Y"),0.986029614300948)

        usd_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_ON, df_TN, df_SN, df_1W, df_2W, df_1M, df_2M, df_3M, df_6M, df_9M, df_1Y], Rate.linearization_enum.log_ds_factor)

        df1 = usd_df_curve.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        # print("result is ",  df1.mid)

        self.assertEqual(round(df1.mid,9), round(0.998657734071825,9))


class Test_cls_swap_point_panel(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360)

        date_of_today = datetime.date(2017, 6, 13)

        df_usd_ON = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,14),"O/N"),0.999968868900009)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,15),"T/N"),0.999937738800022)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,16),"S/N"),0.999907939100022)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,22),"1W"),0.999727254200085)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,29),"2W"),0.999512368799956)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,7,17),"1M"),0.998942551320812)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,8,15),"2M"),0.997910475099995)
        df_usd_3M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,9,15),"3M"),0.996788096599609)
        df_usd_6M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,12,15),"6M"),0.993355657098983)
        df_usd_9M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,3,15),"9M"),0.989821542597184)
        df_usd_1Y = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,6,15),"1Y"),0.986029614300948)

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy, [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M, df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y], Rate.linearization_enum.log_ds_factor)

        df_usd_20170725 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_usd_20170615 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        print("df_usd_20170725 is ",  df_usd_20170725.mid)

        self.assertEqual(round(df_usd_20170725.mid,9), round(0.998657734071825, 9))

        sgd_ccy = Rate.cls_currency("SGD", 365)

        df_sgd_ON = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,14),"O/N"),0.999985489497763)
        df_sgd_TN = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,15),"T/N"),0.999970979621296)
        df_sgd_1W = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,22),"1W"),0.99984358252256)
        df_sgd_1M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,7,17),"1M"),0.999372474118876)
        df_sgd_2M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,8,15),"2M"),0.998656691210744)
        df_sgd_3M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,9,15),"3M"),0.997894307136919)
        df_sgd_6M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,12,15),"6M"),0.995520369701573)
        df_sgd_9M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,3,15),"9M"),0.992886023243647)
        df_sgd_1Y = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,6,15),"1Y"),0.989835750383861)
        df_sgd_2Y = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,6,17),"2Y"),0.975986362472653)

        df_curve_sgd = Rate.cls_discount_factor_curve(usd_ccy, [df_sgd_ON, df_sgd_TN, df_sgd_1W, df_sgd_1M, df_sgd_2M, df_sgd_3M, df_sgd_6M, df_sgd_9M, df_sgd_1Y, df_sgd_2Y], Rate.linearization_enum.log_ds_factor)

        df_sgd_20170725 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017,7,25))
        df_sgd_20170615 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017,6,15))
        # print("df_sgd_20170725 is ",  df_sgd_20170725.mid)

        self.assertEqual(round(df_sgd_20170725.mid,9), round(0.999174965538092,9))

        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000, 2)



        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017,6,15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)

        swap_point_panel_usdsgd = Rate.cls_swap_point_panel(usdsgd, spot_rate_usdsgd, df_curve_usd, df_curve_sgd,False)
        swap_point_list = swap_point_panel_usdsgd.set_swap_point_list()

        #swap_point_20170725 =

        for iter_swap_point in swap_point_list:
            print(iter_swap_point.tenor.label, iter_swap_point.mid * swap_point_panel_usdsgd.swap_point_factor)

        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("O/N").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-0.229998504268636,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("T/N").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-0.230000000172037,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("1W").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-1.15000000056042,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("1M").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-5.49299163299821,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("2M").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-9.87999999721767,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("3M").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-14.8799999861171,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("6M").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-29.6299999672822,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("9M").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-42.2500000343629,9))
        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_from_list_by_tenor_label("1Y").mid * swap_point_panel_usdsgd.swap_point_factor, 9), round(-52.7500000673187,9))


        # print(swap_point_panel_usdsgd.get_swap_point_by_start_maturity(datetime.date(2017,7,25)).mid)

        # print("swap point 20170725 = ", swap_point_panel_usdsgd.spot_rate.mid * ((df_usd_20170725.mid/df_usd_20170615.mid) / (df_sgd_20170725.mid/df_sgd_20170615.mid) - 1 ))

        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_by_start_maturity(datetime.date(2017,7,25)).mid, 9), round(-0.0006703339836723035, 9))

        print(df_sgd_ON.unique_key)

        for iter_swap_point in swap_point_list:
            print(iter_swap_point.unique_key)


# O/N	-0.229998504268636
# T/N	-0.230000000172037
# 1W	-1.15000000056042
# 1M	-5.49299163299821
# 2M	-9.87999999721767
# 3M	-14.8799999861171
# 6M	-29.6299999672822
# 9M	-42.2500000343629
# 1Y	-52.7500000673187
# 2Y	-92.6124637683889
# 3Y	-129.026524587879
# 4Y	-166.725860681756
# 5Y	-217.090843603471
# 6Y	-238.892713981425
# 7Y	-267.544248839398
# 8Y	-351.942049352203
# 9Y	-440.411656980548
# 10Y	-532.33025305504
# 12Y	-721.902727505068
