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
        EURUSD = Rate.cls_currency_pair(EUR,USD, Rate.quotation_mode_enum.base_und,1000)
        self.assertEqual(EURUSD.quotation, "EUR-USD")
        self.assertEqual(EURUSD.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(EURUSD.swap_point_factor, 1000)
        self.assertEqual(EURUSD.day_shift, Rate.date_shift_enum.D2)
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
        RATE1= Rate.cls_rate(6.0,6.2,5.8)
        self.assertEqual(RATE1.mid,6.0)
        self.assertEqual(RATE1.bid,6.2)
        self.assertEqual(RATE1.ask,5.8)
        self.assertEqual(round(RATE1.spread,5),0.2)

        RATE2= Rate.cls_rate()
        RATE2.set_rate_by_mid_spread(1.2,0.3)
        self.assertEqual(RATE2.mid,1.2)
        self.assertEqual(round(RATE2.bid,5),0.9)
        self.assertEqual(round(RATE2.ask,5),1.5)
        self.assertEqual(round(RATE2.spread,5),0.3)

        RATE3= Rate.cls_rate()
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

class Test_cls_on_funding_rate_panel(unittest.TestCase):
    def test_init(self):
        USD= Rate.cls_currency("USD")

        ON_RATE1 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,1), datetime.date(2017,10,2), ""),0.001)
        ON_RATE2 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,2), datetime.date(2017,10,4), ""),0.002)
        ON_RATE3 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,4), datetime.date(2017,10,9), ""),0.003)

        on_list = [ON_RATE1, ON_RATE2, ON_RATE3]

        ON_RATE_DICT = Rate.cls_on_funding_rate_panel(USD,on_list)

        self.assertEqual(ON_RATE_DICT.list_start_date, ON_RATE1.tenor.start_date)
        self.assertEqual(ON_RATE_DICT.list_end_date, ON_RATE3.tenor.maturity_date)

        ON_RATE_LIST_1 = ON_RATE_DICT.get_on_rate_dict_by_start_end_date(ON_RATE1.tenor.start_date,ON_RATE3.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_1[ON_RATE1.tenor.start_date].tenor.maturity_date, ON_RATE1.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_1[ON_RATE1.tenor.start_date].mid, ON_RATE1.mid)

        self.assertEqual(ON_RATE_LIST_1[ON_RATE2.tenor.start_date].tenor.maturity_date, ON_RATE2.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_1[ON_RATE2.tenor.start_date].mid, ON_RATE2.mid)

        self.assertEqual(ON_RATE_LIST_1[ON_RATE3.tenor.start_date].tenor.maturity_date, ON_RATE3.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_1[ON_RATE3.tenor.start_date].mid, ON_RATE3.mid)

        ON_RATE_LIST_2 = ON_RATE_DICT.get_on_rate_dict_by_start_end_date(ON_RATE1.tenor.start_date, datetime.date(2017, 10, 8))
        self.assertEqual(ON_RATE_LIST_2[ON_RATE1.tenor.start_date].tenor.maturity_date, ON_RATE1.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_2[ON_RATE1.tenor.start_date].mid, ON_RATE1.mid)

        self.assertEqual(ON_RATE_LIST_2[ON_RATE2.tenor.start_date].tenor.maturity_date, ON_RATE2.tenor.maturity_date)
        self.assertEqual(ON_RATE_LIST_2[ON_RATE2.tenor.start_date].mid, ON_RATE2.mid)

        self.assertEqual(ON_RATE_LIST_2[ON_RATE3.tenor.start_date].tenor.maturity_date, datetime.date(2017, 10, 8))
        self.assertEqual(ON_RATE_LIST_2[ON_RATE3.tenor.start_date].mid, ON_RATE3.mid)






class Test_cls_discount_factor(unittest.TestCase):
    def test_init(self):
        EUR = Rate.cls_currency("EUR",365)
        one_month=Rate.cls_tenor(datetime.date(2016,12,17),datetime.date(2017,1,17), "1M")
        DF1 = Rate.cls_discount_factor(EUR,one_month,0.997)
        CF1 = DF1.get_capitalized_factor()
        self.assertEqual(DF1.mid,1/CF1.mid)
        DR1 = DF1.get_discount_rate()
        self.assertEqual(1/(DR1.mid * (datetime.date(2017,1,17) - datetime.date(2016,12,17)).days / 365 + 1), DF1.mid)

class Test_cls_market_quote(unittest.TestCase):
    def test_init(self):
        EUR = Rate.cls_currency("EUR", 365)
        today_spot = Rate.cls_tenor(datetime.date(2016, 12, 17), datetime.date(2016, 12, 19), "T/N")
        spot_onemonth =  Rate.cls_tenor(datetime.date(2016,12,19),datetime.date(2017,1,17), "1M")

        DF_t_n = Rate.cls_discount_factor(EUR, today_spot, 0.997)
        MQ1 = Rate.cls_market_quote(EUR, spot_onemonth, 0.2)
        DF1 = MQ1.get_discount_factor(DF_t_n)
        DR1 = MQ1.get_discount_rate(DF_t_n)

        self.assertEqual(DF1.mid, 0.997 / ( 0.2 * (datetime.date(2017,1,17) - datetime.date(2016, 12, 19) ).days / 365 + 1) )
        self.assertEqual(DR1.mid, DF1.get_discount_rate().mid)



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


class Test_cls_market_quote_curve(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360)
        mq_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_ON, mq_TN, mq_SN, mq_1W, mq_2W, mq_1M, mq_2M, mq_3M, mq_6M, mq_9M, mq_1Y])

        mq1 = usd_mq_curve.get_market_quote_by_label("O/N")
        self.assertEqual(round(mq1.mid, 9), round(2.25464634/100, 9))

        mq2 = usd_mq_curve.get_market_quote_by_label("1Y")
        self.assertEqual(round(mq2.mid, 9), round(2.622098069/100, 9))


        df_on = usd_mq_curve.get_discount_factor_by_label('O/N')
        # print("df_on.mid is ", df_on.mid)
        self.assertEqual(round(df_on.mid, 9), round(0.9998121481, 9))

        df_tn = usd_mq_curve.get_discount_factor_by_label('T/N')
        self.assertEqual(round(df_tn.mid, 9), round(0.9997495386, 9))

        df_1m = mq_1M.get_discount_factor(df_tn)
        self.assertEqual(round(df_1m.mid, 9), round(0.9978120546, 9))

        df_2m = mq_2M.get_discount_factor(df_tn)
        self.assertEqual(round(df_2m.mid, 9), round(0.9958490192, 9))

        df_3m = usd_mq_curve.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 9), round(0.9938830249, 9))

        usd_df_curve = usd_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)
        df_6M = usd_df_curve.get_discount_factor_by_label("6M")
        self.assertEqual(round(df_6M.mid, 9), round(0.987466697, 9))

        df_9M = usd_df_curve.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 9), round(0.9808860946, 9))

        df_1Y = usd_df_curve.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 9), round(0.9738593315, 9))


class Test_cls_discount_factor_curve_log_ds_factor(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

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

        usd_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_ON, df_TN, df_SN, df_1W, df_2W, df_1M, df_2M, df_3M, df_6M, df_9M, df_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df1 = usd_df_curve.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        # print("result is ",  df1.mid)

        self.assertEqual(round(df1.mid,9), round(0.998657734071825,9))


class Test_cls_swap_point_panel(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

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

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy, [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M, df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_usd_20170725 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_usd_20170615 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        #print("df_usd_20170725 is ",  df_usd_20170725.mid)

        self.assertEqual(round(df_usd_20170725.mid,9), round(0.998657734071825, 9))

        sgd_ccy = Rate.cls_currency("SGD", 365, Rate.date_shift_enum.D2)

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

        df_curve_sgd = Rate.cls_discount_factor_curve(usd_ccy, [df_sgd_ON, df_sgd_TN, df_sgd_1W, df_sgd_1M, df_sgd_2M, df_sgd_3M, df_sgd_6M, df_sgd_9M, df_sgd_1Y, df_sgd_2Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_sgd_20170725 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017,7,25))
        df_sgd_20170615 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017,6,15))
        # print("df_sgd_20170725 is ",  df_sgd_20170725.mid)

        self.assertEqual(round(df_sgd_20170725.mid,9), round(0.999174965538092,9))

        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000)



        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017,6,15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)

        swap_point_panel_usdsgd = Rate.cls_swap_point_panel(usdsgd, spot_rate_usdsgd, df_curve_usd, df_curve_sgd,False)
        swap_point_panel_usdsgd.refresh_swap_point_list()

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

        self.assertEqual(round(swap_point_panel_usdsgd.get_swap_point_by_maturity(datetime.date(2017, 7, 25)).mid, 9), round(-0.0006703339836723035, 9))

        #print(df_sgd_ON.unique_key)

        #for iter_swap_point in swap_point_list:
        #    print(iter_swap_point.unique_key)


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


class Test_create_swap_point_panel_by_market_quote(unittest.TestCase):
    def test_init(self):
        #today's date = 2018-08-24
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_usd_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_usd_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_usd_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_usd_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_usd_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_usd_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_usd_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_usd_ON, mq_usd_TN, mq_usd_SN, mq_usd_1W, mq_usd_2W, mq_usd_1M, mq_usd_2M, mq_usd_3M, mq_usd_6M, mq_usd_9M, mq_usd_1Y])


        php_ccy = Rate.cls_currency("PHP", 360, Rate.date_shift_enum.D1)
        mq_php_ON = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28),"O/N"),3.60160413/100)
        mq_php_1W = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),0.274157119/100)
        mq_php_1M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),3.603877329/100)
        mq_php_2M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),4.230839063/100)
        mq_php_3M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),4.514130365/100)
        mq_php_6M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),4.737593254/100)
        mq_php_9M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),4.903449646/100)
        mq_php_1Y = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),4.964164241/100)

        php_mq_curve = Rate.cls_market_quote_curve(php_ccy, [mq_php_ON, mq_php_1W, mq_php_1M, mq_php_2M, mq_php_3M, mq_php_6M, mq_php_9M, mq_php_1Y])


        mq1 = php_mq_curve.get_market_quote_by_label("O/N")
        self.assertEqual(round(mq1.mid, 9), round(3.60160413/100, 9))

        mq2 = php_mq_curve.get_market_quote_by_label("1Y")
        self.assertEqual(round(mq2.mid, 9), round(4.964164241/100, 9))


        df_on = php_mq_curve.get_discount_factor_by_label('O/N')
        # print("df_on.mid is ", df_on.mid)
        self.assertEqual(round(df_on.mid, 9), round(0.999599981841894, 9))

        df_1m = mq_php_1M.get_discount_factor(df_on)
        self.assertEqual(round(df_1m.mid, 9), round(0.996507481499024, 9))

        df_2m = mq_php_2M.get_discount_factor(df_on)
        self.assertEqual(round(df_2m.mid, 9), round(0.992369138640949, 9))

        df_3m = php_mq_curve.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 9), round(0.98819999705213, 9))

        php_df_curve = php_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)
        df_6M = php_df_curve.get_discount_factor_by_label("6M")
        self.assertEqual(round(df_6M.mid, 9), round(0.975967546924571, 9))

        df_9M = php_df_curve.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 9), round(0.963762945208683, 9))

        df_1Y = php_df_curve.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 9), round(0.951699871253031, 9))


        usdphp_pair = Rate.cls_currency_pair(usd_ccy, php_ccy, Rate.quotation_mode_enum.base_und, 1000)

        usdphp_spot_rate = Rate.cls_fx_spot_rate(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28)), 53.478)

        swp_panel_usdphp = Rate.create_swap_point_panel_by_market_quote_curves(usdphp_pair, usdphp_spot_rate, usd_mq_curve, php_mq_curve, Rate.linearization_enum.log_ds_factor, Rate.linearization_enum.log_ds_factor)
        #print("und spot shift is ", swp_panel_usdphp.df_curve_und_ccy.spot_date_shift)

        swp_panel_usdphp.refresh_swap_point_list()

        swap_on = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('O/N')
        self.assertEqual(round(swap_on.mid, 9), round(7.99999999922818/1000, 9))

        swap_1w = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('1W')
        self.assertEqual(round(swap_1w.mid, 9), round(-20.499999999565 / 1000, 9))

        swap_1m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('1M')
        self.assertEqual(round(swap_1m.mid, 9), round(62.0000000199923 / 1000, 9))

        swap_2m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('2M')
        self.assertEqual(round(swap_2m.mid, 9), round(179.49999998784 / 1000, 9))

        swap_3m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('3M')
        self.assertEqual(round(swap_3m.mid, 9), round(299.499999950342 / 1000, 9))

        swap_6m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('6M')
        self.assertEqual(round(swap_6m.mid, 9), round(621.999999976751 / 1000, 9))

        swap_9m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('9M')
        self.assertEqual(round(swap_9m.mid, 9), round(942.000000096037 / 1000, 9))

        swap_1y = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label('1Y')
        self.assertEqual(round(swap_1y.mid, 9), round(1236.9999998302 / 1000, 9))


class Test_market_quote_curve_dict(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_usd_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_usd_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_usd_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_usd_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_usd_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_usd_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_usd_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_usd_ON, mq_usd_TN, mq_usd_SN, mq_usd_1W, mq_usd_2W, mq_usd_1M, mq_usd_2M, mq_usd_3M, mq_usd_6M, mq_usd_9M, mq_usd_1Y])


        php_ccy = Rate.cls_currency("PHP", 360, Rate.date_shift_enum.D1)
        mq_php_ON = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28),"O/N"),3.60160413/100)
        mq_php_1W = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),0.274157119/100)
        mq_php_1M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),3.603877329/100)
        mq_php_2M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),4.230839063/100)
        mq_php_3M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),4.514130365/100)
        mq_php_6M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),4.737593254/100)
        mq_php_9M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),4.903449646/100)
        mq_php_1Y = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),4.964164241/100)

        php_mq_curve = Rate.cls_market_quote_curve(php_ccy, [mq_php_ON, mq_php_1W, mq_php_1M, mq_php_2M, mq_php_3M, mq_php_6M, mq_php_9M, mq_php_1Y])

        usdphp_pair = Rate.cls_currency_pair(usd_ccy, php_ccy, Rate.quotation_mode_enum.base_und, 1000)

        usdphp_spot_rate = Rate.cls_fx_spot_rate(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28)), 53.478)

        mq_curve_dict = Rate.cls_market_quote_curve_dict(datetime.date(2018, 8,24))

        mq_curve_dict.add_curve_to_dict(usd_ccy.label, usd_mq_curve)
        mq_curve_dict.add_curve_to_dict(php_ccy.label, php_mq_curve)


        df_curve_dict = mq_curve_dict.get_discount_factor_curve_dict(Rate.linearization_enum.log_ds_factor)

        df_curve_php = df_curve_dict.get_curve_by_currency_label(php_ccy.label)


        df_on = df_curve_php.get_discount_factor_by_label("O/N")
        # print("df_on.mid is ", df_on.mid)
        self.assertEqual(round(df_on.mid, 9), round(0.999599981841894, 9))

        df_1m = df_curve_php.get_discount_factor_by_label("1M")
        self.assertEqual(round(df_1m.mid, 9), round(0.996507481499024, 9))

        df_2m = df_curve_php.get_discount_factor_by_label("2M")
        self.assertEqual(round(df_2m.mid, 9), round(0.992369138640949, 9))

        df_3m = df_curve_php.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 9), round(0.98819999705213, 9))

        php_df_curve = php_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)
        df_6m = df_curve_php.get_discount_factor_by_label("6M")
        self.assertEqual(round(df_6m.mid, 9), round(0.975967546924571, 9))

        df_9M = df_curve_php.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 9), round(0.963762945208683, 9))

        df_1Y = df_curve_php.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 9), round(0.951699871253031, 9))

        swp_panel_usdphp = df_curve_dict.get_swap_point_panel_by_currency_pair(usdphp_pair, usdphp_spot_rate)

        swap_on = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("O/N")
        self.assertEqual(round(swap_on.mid, 9), round(7.99999999922818/1000, 9))

        swap_1w = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("1W")
        self.assertEqual(round(swap_1w.mid, 9), round(-20.499999999565 / 1000, 9))

        swap_1m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("1M")
        self.assertEqual(round(swap_1m.mid, 9), round(62.0000000199923 / 1000, 9))

        swap_2m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("2M")
        self.assertEqual(round(swap_2m.mid, 9), round(179.49999998784 / 1000, 9))

        swap_3m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("3M")
        self.assertEqual(round(swap_3m.mid, 9), round(299.499999950342 / 1000, 9))

        swap_6m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("6M")
        self.assertEqual(round(swap_6m.mid, 9), round(621.999999976751 / 1000, 9))

        swap_9m = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("9M")
        self.assertEqual(round(swap_9m.mid, 9), round(942.000000096037 / 1000, 9))

        swap_1y = swp_panel_usdphp.get_swap_point_from_list_by_tenor_label("1Y")
        self.assertEqual(round(swap_1y.mid, 9), round(1236.9999998302 / 1000, 9))


class Test_get_und_df_curve_by_swap_point_list1(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        sgd_ccy = Rate.cls_currency("SGD", 365, Rate.date_shift_enum.D2)
        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000)

        date_of_today = datetime.date(2017, 6, 13)

        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)


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

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy, [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M, df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        swap_point_panel_usdsgd = Rate.cls_swap_point_panel(usdsgd, spot_rate_usdsgd, df_curve_usd, None, False)


        swap_point_ON = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(date_of_today, datetime.date(2017,6,14), "O/N"), -0.229998504268636/10000)
        swap_point_TN = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017,6,14), datetime.date(2017, 6, 15), "T/N"), -0.230000000172037 / 10000)
        swap_point_1W = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2017, 6, 22), "1W"), -1.15000000056042 / 10000)
        swap_point_1M = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2017, 7, 17), "1M"), -5.49299163299821 / 10000)
        swap_point_2M = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2017, 8, 15), "2M"), -9.87999999721767 / 10000)
        swap_point_3M = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2017, 9, 15), "3M"), -14.8799999861171 / 10000)
        swap_point_6M = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2017, 12, 15), "6M"), -29.6299999672822 / 10000)
        swap_point_9M = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2018, 3, 15), "9M"), -42.2500000343629 / 10000)
        swap_point_1Y = Rate.cls_swap_point(usdsgd, Rate.cls_tenor(datetime.date(2017, 6, 15), datetime.date(2018, 6, 15), "1Y"), -52.7500000673187 / 10000)

        swap_point_panel_usdsgd.fx_rate_list = [swap_point_ON, swap_point_TN, swap_point_1W, swap_point_1M, swap_point_2M, swap_point_3M, swap_point_6M, swap_point_9M, swap_point_1Y]

        df_curve_sgd = swap_point_panel_usdsgd.get_und_df_curve_by_swap_point_list(Rate.linearization_enum.log_ds_factor)

        df_sgd_ON=df_curve_sgd.get_discount_factor_by_label("O/N")
        self.assertEqual(round(df_sgd_ON.value, 9), round(0.999985489497763, 9))

        df_sgd_TN=df_curve_sgd.get_discount_factor_by_label("T/N")
        self.assertEqual(round(df_sgd_TN.value, 9), round(0.999970979621296, 9))

        df_sgd_1W=df_curve_sgd.get_discount_factor_by_label("1W")
        self.assertEqual(round(df_sgd_1W.value, 9), round(0.99984358252256, 9))

        df_sgd_1M=df_curve_sgd.get_discount_factor_by_label("1M")
        self.assertEqual(round(df_sgd_1M.value, 9), round(0.999372474118876, 9))

        df_sgd_2M=df_curve_sgd.get_discount_factor_by_label("2M")
        self.assertEqual(round(df_sgd_2M.value, 9), round(0.998656691210744, 9))

        df_sgd_3M=df_curve_sgd.get_discount_factor_by_label("3M")
        self.assertEqual(round(df_sgd_3M.value, 9), round(0.997894307136919, 9))

        df_sgd_6M=df_curve_sgd.get_discount_factor_by_label("6M")
        self.assertEqual(round(df_sgd_6M.value, 9), round(0.995520369701573, 9))

        df_sgd_9M=df_curve_sgd.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_sgd_9M.value, 9), round(0.992886023243647, 9))

        df_sgd_1Y=df_curve_sgd.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_sgd_1Y.value, 9), round(0.989835750383861, 9))


        # df_sgd_ON = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,14),"O/N"),0.999985489497763)
        # df_sgd_TN = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,15),"T/N"),0.999970979621296)
        # df_sgd_1W = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,6,22),"1W"),0.99984358252256)
        # df_sgd_1M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,7,17),"1M"),0.999372474118876)
        # df_sgd_2M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,8,15),"2M"),0.998656691210744)
        # df_sgd_3M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,9,15),"3M"),0.997894307136919)
        # df_sgd_6M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2017,12,15),"6M"),0.995520369701573)
        # df_sgd_9M = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,3,15),"9M"),0.992886023243647)
        # df_sgd_1Y = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,6,15),"1Y"),0.989835750383861)
        # df_sgd_2Y = Rate.cls_discount_factor(sgd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,6,17),"2Y"),0.975986362472653)


class Test_get_und_df_curve_by_swap_point_list2(unittest.TestCase):
    def test_init(self):
        date_of_today = datetime.date(2018, 9, 28)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        eur_ccy = Rate.cls_currency("EUR", 360, Rate.date_shift_enum.D2)

        eurusd_pair = Rate.cls_currency_pair(usd_ccy, eur_ccy, Rate.quotation_mode_enum.und_base, 10000)

        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2018, 10, 2))
        spot_rate_eurusd = Rate.cls_fx_spot_rate(eurusd_pair, spot_tenor, 1.16215)


        df_usd_ON = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,1),"O/N"),0.999811008)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,2),"T/N"),0.9997480186)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,3),"S/N"),0.9996859615)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,9),"1W"),0.9993124755)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,16),"2W"),0.9988742667)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,11,2),"1M"),0.9977989698)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,12,3),"2M"),0.9957647212)
        df_usd_3M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,1,2),"3M"),0.9936637053)
        df_usd_6M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,4,2),"6M"),0.9869975221)
        df_usd_9M = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,7,2),"9M"),0.9798946665)
        df_usd_1Y = Rate.cls_discount_factor(usd_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,10,2),"1Y"),0.9724126507)

        usd_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M, df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)


        eur_ccy = Rate.cls_currency("EUR", 360, Rate.date_shift_enum.D2)
        df_eur_ON = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,1),"O/N"),1.0001377931)
        df_eur_TN = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,2),"T/N"),1.0001556803)
        df_eur_SN = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,3),"S/N"),1.0001736295)
        df_eur_1W = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,9),"1W"),1.0002705088)
        df_eur_2W = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,16),"2W"),1.0003735891)
        df_eur_3W = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,10,23),"3W"),1.0004740622)
        df_eur_1M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,11,2),"1M"),1.0006245844)
        df_eur_2M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2018,12,3),"2M"),1.0010292501)
        df_eur_3M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,1,2),"3M"),1.0020358073)
        df_eur_4M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,2,4),"4M"),1.0023891343)
        df_eur_5M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,3,4),"5M"),1.0026677673)
        df_eur_6M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,4,2),"6M"),1.0031181791)
        df_eur_7M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,5,2),"7M"),1.0034406885)
        df_eur_8M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,6,3),"8M"),1.0037869007)
        df_eur_9M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,7,2),"9M"),1.004214711)
        df_eur_10M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,8,2),"10M"),1.0044993232)
        df_eur_11M = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,9,3),"11M"),1.0048246562)
        df_eur_1Y = Rate.cls_discount_factor(eur_ccy,Rate.cls_tenor(date_of_today,datetime.date(2019,10,2),"1Y"),1.0051730784)

        eur_df_curve = Rate.cls_discount_factor_curve(usd_ccy, [df_eur_ON, df_eur_TN, df_eur_SN, df_eur_1W, df_eur_2W, df_eur_3W, df_eur_1M, df_eur_2M, df_eur_3M, df_eur_4M, df_eur_5M,
                                                                df_eur_6M, df_eur_7M, df_eur_8M, df_eur_9M, df_eur_10M, df_eur_11M, df_eur_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        swap_point_panel_eurusd = Rate.cls_swap_point_panel(eurusd_pair, spot_rate_eurusd, usd_df_curve, None, False)


        swap_point_ON = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(date_of_today, df_eur_ON.maturity_date, "O/N"), 3.7969028849 / eurusd_pair.swap_point_factor)
        swap_point_TN = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(df_eur_ON.maturity_date, spot_rate_eurusd.maturity_date, "T/N"), 0.94 / eurusd_pair.swap_point_factor)
        swap_point_SN = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_SN.maturity_date, "S/N"), 0.9300000001 / eurusd_pair.swap_point_factor)
        swap_point_1W = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_1W.maturity_date, "1W"), 6.3999999989 / eurusd_pair.swap_point_factor)
        swap_point_2W = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_2W.maturity_date, "2W"), 12.6999999983 / eurusd_pair.swap_point_factor)
        swap_point_3W = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_3W.maturity_date, "3W"), 19.0300000018 / eurusd_pair.swap_point_factor)
        swap_point_1M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_1M.maturity_date, "1M"), 28.1599999987 / eurusd_pair.swap_point_factor)
        swap_point_2M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_2M.maturity_date, "2M"), 56.6800000045 / eurusd_pair.swap_point_factor)
        swap_point_3M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_3M.maturity_date, "3M"), 93.1400000145 / eurusd_pair.swap_point_factor)
        swap_point_4M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_4M.maturity_date, "4M"), 126.2299999826 / eurusd_pair.swap_point_factor)
        swap_point_5M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_5M.maturity_date, "5M"), 154.1299999989 / eurusd_pair.swap_point_factor)
        swap_point_6M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_6M.maturity_date, "6M"), 185.0000000216 / eurusd_pair.swap_point_factor)
        swap_point_7M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_7M.maturity_date, "7M"), 216.949999846 / eurusd_pair.swap_point_factor)
        swap_point_8M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_8M.maturity_date, "8M"), 251.1499999971 / eurusd_pair.swap_point_factor)
        swap_point_9M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_9M.maturity_date, "9M"), 283.5799999913 / eurusd_pair.swap_point_factor)
        swap_point_10M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_10M.maturity_date, "10M"), 317.7500000352 / eurusd_pair.swap_point_factor)
        swap_point_11M = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_11M.maturity_date, "11M"), 353.5000000018 / eurusd_pair.swap_point_factor)
        swap_point_1Y = Rate.cls_swap_point(eurusd_pair, Rate.cls_tenor(spot_rate_eurusd.maturity_date, df_eur_1Y.maturity_date, "1Y"), 386.6300000163 / eurusd_pair.swap_point_factor)

        swap_point_panel_eurusd.fx_rate_list = [swap_point_ON, swap_point_TN, swap_point_SN, swap_point_1W, swap_point_2W, swap_point_3W,
                                                swap_point_1M, swap_point_2M, swap_point_3M, swap_point_4M, swap_point_5M, swap_point_6M,
                                                swap_point_7M, swap_point_8M, swap_point_9M, swap_point_10M, swap_point_11M, swap_point_1Y]

        df_curve_eur_cal = swap_point_panel_eurusd.get_und_df_curve_by_swap_point_list(Rate.linearization_enum.log_ds_factor)


        df_on = eur_df_curve.get_discount_factor_by_label("O/N")
        self.assertEqual(round(df_on.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("O/N").value, 8))

        df_tn = eur_df_curve.get_discount_factor_by_label("T/N")
        self.assertEqual(round(df_tn.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("T/N").value, 8))

        df_sn = eur_df_curve.get_discount_factor_by_label("S/N")
        self.assertEqual(round(df_sn.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("S/N").value, 8))

        df_1w = eur_df_curve.get_discount_factor_by_label("1W")
        self.assertEqual(round(df_1w.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("1W").value, 8))

        df_2w = eur_df_curve.get_discount_factor_by_label("2W")
        self.assertEqual(round(df_2w.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("2W").value, 8))

        df_3w = eur_df_curve.get_discount_factor_by_label("3W")
        self.assertEqual(round(df_3w.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("3W").value, 8))

        df_1m = eur_df_curve.get_discount_factor_by_label("1M")
        self.assertEqual(round(df_1m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("1M").value, 8))

        df_2m = eur_df_curve.get_discount_factor_by_label("2M")
        self.assertEqual(round(df_2m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("2M").value, 8))

        df_3m = eur_df_curve.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("3M").value, 8))

        df_4m = eur_df_curve.get_discount_factor_by_label('4M')
        self.assertEqual(round(df_4m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("4M").value, 8))

        df_5m = eur_df_curve.get_discount_factor_by_label('5M')
        self.assertEqual(round(df_5m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("5M").value, 8))

        df_6m = eur_df_curve.get_discount_factor_by_label('6M')
        self.assertEqual(round(df_6m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("6M").value, 8))

        df_7m = eur_df_curve.get_discount_factor_by_label('7M')
        self.assertEqual(round(df_7m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("7M").value, 8))

        df_8m = eur_df_curve.get_discount_factor_by_label('8M')
        self.assertEqual(round(df_8m.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("8M").value, 8))

        df_9M = eur_df_curve.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("9M").value, 8))

        df_10M = eur_df_curve.get_discount_factor_by_label("10M")
        self.assertEqual(round(df_10M.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("10M").value, 8))

        df_11M = eur_df_curve.get_discount_factor_by_label("11M")
        self.assertEqual(round(df_11M.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("11M").value, 8))

        df_1Y = eur_df_curve.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 8), round(df_curve_eur_cal.get_discount_factor_by_label("1Y").value, 8))



class Test_get_und_df_curve_by_swap_point_list3(unittest.TestCase):
    def test_init(self):
        date_of_today = datetime.date(2018, 8, 24)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_usd_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_usd_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_usd_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_usd_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_usd_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_usd_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_usd_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_usd_ON, mq_usd_TN, mq_usd_SN, mq_usd_1W, mq_usd_2W, mq_usd_1M, mq_usd_2M, mq_usd_3M, mq_usd_6M, mq_usd_9M, mq_usd_1Y])
        usd_df_curve = usd_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)


        php_ccy = Rate.cls_currency("PHP", 360, Rate.date_shift_enum.D1)
        mq_php_ON = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28),"O/N"),3.60160413/100)
        mq_php_1W = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),0.274157119/100)
        mq_php_1M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),3.603877329/100)
        mq_php_2M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),4.230839063/100)
        mq_php_3M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),4.514130365/100)
        mq_php_6M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),4.737593254/100)
        mq_php_9M = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),4.903449646/100)
        mq_php_1Y = Rate.cls_market_quote(php_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),4.964164241/100)

        php_mq_curve = Rate.cls_market_quote_curve(php_ccy, [mq_php_ON, mq_php_1W, mq_php_1M, mq_php_2M, mq_php_3M, mq_php_6M, mq_php_9M, mq_php_1Y])
        php_df_curve = php_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)

        usdphp_pair = Rate.cls_currency_pair(usd_ccy, php_ccy, Rate.quotation_mode_enum.base_und, 1000)

        usdphp_spot_rate = Rate.cls_fx_spot_rate(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,28)), 53.478)


        swap_point_panel_usdphp = Rate.cls_swap_point_panel(usdphp_pair, usdphp_spot_rate, usd_df_curve, None, False)


        swap_point_ON = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(date_of_today, datetime.date(2018,8,28), "O/N"), 7.99999999922818/1000)
        swap_point_1W = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2018, 9, 4), "1W"), -20.499999999565 / 1000)
        swap_point_1M = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2018, 9, 28), "1M"), 62.0000000199923 / 1000)
        swap_point_2M = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2018, 10, 29), "2M"), 179.49999998784 / 1000)
        swap_point_3M = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2018, 11, 28), "3M"), 299.499999950342 / 1000)
        swap_point_6M = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2019, 2, 28), "6M"), 621.999999976751 / 1000)
        swap_point_9M = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2019, 5, 28), "9M"), 942.000000096037 / 1000)
        swap_point_1Y = Rate.cls_swap_point(usdphp_pair, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2019, 8, 28), "1Y"), 1236.9999998302  / 1000)

        swap_point_panel_usdphp.fx_rate_list = [swap_point_ON, swap_point_1W, swap_point_1M, swap_point_2M, swap_point_3M, swap_point_6M, swap_point_9M, swap_point_1Y]

        df_curve_php_cal = swap_point_panel_usdphp.get_und_df_curve_by_swap_point_list(Rate.linearization_enum.log_ds_factor)


        df_on = php_df_curve.get_discount_factor_by_label("O/N")
        self.assertEqual(round(df_on.mid, 9), round(0.999599981841894, 9))
        self.assertEqual(round(df_on.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("O/N").value, 9))

        df_1w = php_df_curve.get_discount_factor_by_label("1W")
        self.assertEqual(round(df_1w.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("1W").value, 9))

        df_1m = php_df_curve.get_discount_factor_by_label("1M")
        self.assertEqual(round(df_1m.mid, 9), round(0.996507481499024, 9))
        self.assertEqual(round(df_1m.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("1M").value, 9))

        df_2m = php_df_curve.get_discount_factor_by_label("2M")
        self.assertEqual(round(df_2m.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("2M").value, 9))

        df_3m = php_df_curve.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 9), round(0.98819999705213, 9))
        self.assertEqual(round(df_3m.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("3M").value, 9))

        df_6m = php_df_curve.get_discount_factor_by_label('6M')
        self.assertEqual(round(df_6m.mid, 9), round(0.975967546924571, 9))
        self.assertEqual(round(df_6m.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("6M").value, 9))

        df_9M = php_df_curve.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 9), round(0.963762945208683, 9))
        self.assertEqual(round(df_9M.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("9M").value, 9))

        df_1Y = php_df_curve.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 9), round(0.951699871253031, 9))
        self.assertEqual(round(df_1Y.mid, 9), round(df_curve_php_cal.get_discount_factor_by_label("1Y").value, 9))


class Test_get_discounted_factor_from_market_quote_over_1Y_1(unittest.TestCase):

    def test_init(self):
        spot_date = datetime.date(2016, 9, 7)
        interpayment_date = datetime.date(2017, 3, 7)
        maturity_date = datetime.date(2018, 3, 7)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        df_spot_interpayment = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, interpayment_date, "6M"), 0.995536183)
        market_quote_spot_maturity = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, "18M"),  1.011792604/100)

        df_spot_maturity = Rate.get_discounted_factor_spot_maturity_from_market_quote_over_1Y(df_spot_interpayment, market_quote_spot_maturity)

        #print("df_spot_maturity={df_spot_maturity}".format(df_spot_maturity=df_spot_maturity.value))
        self.assertEqual(round(df_spot_maturity.mid, 9), round(0.984832779, 9))


class Test_get_discounted_factor_from_market_quote_over_1Y_2(unittest.TestCase):

    def test_init(self):
        date_of_today = datetime.date(2016, 9, 5)
        spot_date = datetime.date(2016, 9, 7)
        interpayment_date = datetime.date(2017, 3, 7)
        maturity_date = datetime.date(2018, 3, 7)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        df_today_spot = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, spot_date, "T/N"), 0.999961162537631)
        market_quote_spot_backwardshifteddate = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(spot_date, interpayment_date, "6M"), 0.891811923 / 100)
        market_quote_spot_maturity = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, "18M"),  1.011792604 / 100)

        df_today_maturity = Rate.get_discounted_factor_today_maturity_from_market_quote_over_1Y(df_today_spot, market_quote_spot_backwardshifteddate, market_quote_spot_maturity)

        #print("df_spot_maturity={df_spot_maturity}".format(df_spot_maturity=df_spot_maturity.value))
        self.assertEqual(round(df_today_maturity.mid, 9), round(0.984794530399031, 9))


class Test_get_discounted_factor_spot_maturity_from_market_quote_over_1Ys(unittest.TestCase):

    def test_init(self):
        spot_date = datetime.date(2016, 9, 7)
        interpayment_date = datetime.date(2017, 3, 7)
        maturity_date = datetime.date(2018, 3, 7)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        df_spot_interpayment = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, interpayment_date, "6M"), 0.995536183)
        market_quote_spot_maturity = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, "18M"),  1.011792604/100)

        df_spot_maturity = Rate.get_discounted_factor_spot_maturity_from_market_quote_over_1Ys([df_spot_interpayment], market_quote_spot_maturity)

        #print("df_spot_maturity={df_spot_maturity}".format(df_spot_maturity=df_spot_maturity.value))
        self.assertEqual(round(df_spot_maturity.mid, 9), round(0.984832779, 9))


class Test_get_discount_factor_curve_from_market_quote_curve_dict(unittest.TestCase):
    def test_init(self):

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_usd_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_usd_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_usd_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_usd_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_usd_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_usd_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_usd_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        mq_usd_18M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2020, 2, 28), "18M"), 2.722778208 / 100)
        mq_usd_2Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2020, 8, 28), "2Y"), 2.776357766 / 100)

        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_usd_ON, mq_usd_TN, mq_usd_SN, mq_usd_1W, mq_usd_2W, mq_usd_1M, mq_usd_2M, mq_usd_3M, mq_usd_6M, mq_usd_9M, mq_usd_1Y, mq_usd_18M, mq_usd_2Y])


        df_on = usd_mq_curve.get_discount_factor_by_label('O/N')
        # print("df_on.mid is ", df_on.mid)
        self.assertEqual(round(df_on.mid, 9), round(0.9998121481, 9))

        df_tn = usd_mq_curve.get_discount_factor_by_label('T/N')
        self.assertEqual(round(df_tn.mid, 9), round(0.9997495386, 9))

        df_1m = mq_usd_1M.get_discount_factor(df_tn)
        self.assertEqual(round(df_1m.mid, 9), round(0.9978120546, 9))

        df_2m = mq_usd_2M.get_discount_factor(df_tn)
        self.assertEqual(round(df_2m.mid, 9), round(0.9958490192, 9))

        df_3m = usd_mq_curve.get_discount_factor_by_label('3M')
        self.assertEqual(round(df_3m.mid, 9), round(0.9938830249, 9))


        usd_df_curve = usd_mq_curve.get_discount_factor_curve(Rate.linearization_enum.log_ds_factor)

        df_6M = usd_df_curve.get_discount_factor_by_label("6M")
        self.assertEqual(round(df_6M.mid, 9), round(0.987466697, 9))

        df_9M = usd_df_curve.get_discount_factor_by_label("9M")
        self.assertEqual(round(df_9M.mid, 9), round(0.9808860946, 9))

        df_1Y = usd_df_curve.get_discount_factor_by_label("1Y")
        self.assertEqual(round(df_1Y.mid, 9), round(0.9738593315, 9))

        df_18M = usd_df_curve.get_discount_factor_by_label("18M")
        self.assertEqual(round(df_18M.mid, 9), round(0.9595191031, 9))

        df_2Y = usd_df_curve.get_discount_factor_by_label("2Y")
        self.assertEqual(round(df_2Y.mid, 9), round(0.9456441548, 9))



class Test_get_market_quote_list_backwardshifted(unittest.TestCase):
    def test_init(self):
        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,24),datetime.date(2018,8,27),"O/N"),2.25464634/100)
        mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,27),datetime.date(2018,8,28),"T/N"),2.254506667/100)
        mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,8,29),"S/N"),2.54503811/100)
        mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,4),"1W"),2.246456453/100)
        mq_usd_2W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,11),"2W"),2.248441218/100)
        mq_usd_1M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,9,28),"1M"),2.25491505/100)
        mq_usd_2M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,10,29),"2M"),2.274258118/100)
        mq_usd_3M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2018,11,28),"3M"),2.309720822/100)
        mq_usd_6M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,2,28),"6M"),2.433666541/100)
        mq_usd_9M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,5,28),"9M"),2.535959205/100)
        mq_usd_1Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8,28),datetime.date(2019,8,28),"1Y"),2.622098069/100)

        mq_usd_18M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2020, 2, 28), "18M"), 2.722778208 / 100)
        mq_usd_2Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2020, 8, 28), "2Y"), 2.776357766 / 100)
        mq_usd_30M = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2021, 2, 28), "30M"), 2.303030 / 100)
        mq_usd_3Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2021, 8, 28), "3Y"), 2.3333 / 100)
        mq_usd_4Y = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018, 8, 28), datetime.date(2022, 8, 28), "4Y"), 2.4444 / 100)


        usd_mq_curve = Rate.cls_market_quote_curve(usd_ccy, [mq_usd_ON, mq_usd_TN, mq_usd_SN, mq_usd_1W, mq_usd_2W, mq_usd_1M, mq_usd_2M, mq_usd_3M, mq_usd_6M, mq_usd_9M, mq_usd_1Y, mq_usd_18M, mq_usd_2Y, mq_usd_30M, mq_usd_3Y, mq_usd_4Y])

        result_list = usd_mq_curve.get_market_quote_list_backwardshifted("4Y", [])

        # for mq_iter in result_list:
        #     print(mq_iter.label)

        self.assertEqual(result_list[0].label, "1Y")
        self.assertEqual(result_list[1].label, "2Y")
        self.assertEqual(result_list[2].label, "3Y")


        result_list1 = usd_mq_curve.get_market_quote_list_backwardshifted("30M", [])

        self.assertEqual(result_list1[0].label, "6M")
        self.assertEqual(result_list1[1].label, "18M")

