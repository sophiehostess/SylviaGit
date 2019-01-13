#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime

import Rate2 as Rate
import PVBP as PVBP
import Trade as Trade



class Test_cls_fx_forward_zcdv01(unittest.TestCase):

    def test_init(self):

        test_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
                                           counterparty = "ABC123",
                                           portfolio = "PORT789",
                                           trade_date = datetime.date(2013,12,30),
                                           maturity_date = datetime.date(2020,12,22),
                                           base_ccy_input = "USD",
                                           quotation_input = "USD-MYR",
                                           ccy1_input = "USD",
                                           ccy1_notional = 377620.494408476,
                                           ccy2_input = "MYR",
                                           ccy2_notional = -1283154.44)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        myr_ccy = Rate.cls_currency("MYR", 365, Rate.date_shift_enum.D2)

        date_of_today = datetime.date(2018, 3, 28)
        spot_date =  datetime.date(2018, 3, 30)

        maturity_date = datetime.date(2020,12,22)


        usdmyr = Rate.cls_currency_pair(usd_ccy, myr_ccy, Rate.quotation_mode_enum.base_und, 10000)


        spot_tenor = Rate.cls_tenor(date_of_today, spot_date)
        spot_rate_usdmyr = Rate.cls_fx_spot_rate(usdmyr, spot_tenor, 3.859)

        df_usd_t_s = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, spot_date, ""), 0.999865742800009)
        df_usd_t_m = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, maturity_date, ""), 0.931371789001951)
        df_myr_t_s = Rate.cls_discount_factor(myr_ccy, Rate.cls_tenor(date_of_today, spot_date, ""), 0.999873241744889)
        df_myr_t_m = Rate.cls_discount_factor(myr_ccy, Rate.cls_tenor(date_of_today, maturity_date, ""), 0.912340176636065)

        bucket_date1 = datetime.date(2018, 3, 29)
        bucket_date2 = datetime.date(2018, 4, 4)
        bucket_date3 = datetime.date(2020, 3, 28)
        bucket_date4 = datetime.date(2021, 3, 28)


        dv01 = PVBP.cls_fx_forward_zcdv01(test_trade,
                                          df_usd_t_s,
                                          df_usd_t_m,
                                          df_myr_t_s,
                                          df_myr_t_m,
                                          spot_rate_usdmyr,
                                          bucket_date1,
                                          bucket_date2,
                                          bucket_date3,
                                          bucket_date4,
                                          date_of_today)


        self.assertEqual(round(dv01.pvbp_d_pl_base_d_zc_base_t_s , 4), round(0.1685, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_base_d_zc_base_t_m , 4), round(-90.9912, 4))

        self.assertEqual(round(dv01.pvbp_in_base_by_1bp_base, 4), round(-90.8227, 4))

        self.assertEqual(round(dv01.pvbp_d_pl_und_d_zc_und_t_s , 4), round(-0.6414, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_und_d_zc_und_t_m , 4), round(292.6171, 4))

        self.assertEqual(round(dv01.pvbp_in_und_by_1bp_und, 4), round(291.9757, 4))

        self.assertEqual(round(dv01.pvbp_d_pl_base_by_d_zc_base_f1, 4), round(0.1404, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_base_by_d_zc_base_f2, 4), round(0.0281, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_base_by_d_zc_base_f3, 4), round(-23.9319, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_base_by_d_zc_base_f4, 4), round(-67.0592, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_und_by_d_zc_und_f1, 4), round(-0.5345, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_und_by_d_zc_und_f2, 4), round(-0.1069, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_und_by_d_zc_und_f3, 4), round(76.9623, 4))
        self.assertEqual(round(dv01.pvbp_d_pl_und_by_d_zc_und_f4, 4), round(215.6548, 4))



class Test_create_fx_forward_zcdv01_from_df_curves(unittest.TestCase):

    def test_init(self):

        test_trade = Trade.create_fx_trade(trade_uti="0025N400023785337",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2019, 1, 2),
                                           maturity_date=datetime.date(2019, 3, 7),
                                           base_ccy_input="USD",
                                           quotation_input="NZD-USD",
                                           ccy1_input="NZD",
                                           ccy1_notional=-20000000,
                                           ccy2_input="USD",
                                           ccy2_notional=13389946)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        nzd_ccy = Rate.cls_currency("NZD", 360, Rate.date_shift_enum.D2)

        date_of_today = datetime.date(2019, 1, 11)
        spot_date = datetime.date(2019, 1, 15)

        maturity_date = datetime.date(2019, 3, 7)

        nzdusd = Rate.cls_currency_pair(usd_ccy, nzd_ccy, Rate.quotation_mode_enum.und_base, 10000)

        spot_tenor = Rate.cls_tenor(date_of_today, spot_date)
        spot_rate_nzdusd = Rate.cls_fx_spot_rate(nzdusd, spot_tenor, 0.6826, quotation_mode=Rate.quotation_mode_enum.und_base)

        df_usd_ON = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 14), "O/N"), 0.9997584933)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 15), "T/N"), 0.9996780041)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 16), "S/N"), 0.9995965378)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 22), "1W"), 0.9991093781)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 29), "2W"), 0.9985445699)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 2, 15), "1M"), 0.9971887494)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 3, 15), "2M"), 0.9950367968)

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M,
                                                       df_usd_2M],
                                                      Rate.linearization_enum.log_ds_factor)


        df_nzd_ON = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 14), "O/N"), 0.9998302406)
        df_nzd_TN = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 15), "T/N"), 0.9997702507)
        df_nzd_1W = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 22), "1W"), 0.9993333158)
        df_nzd_2W = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 1, 29), "2W"), 0.9988927351)
        df_nzd_3W = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 2, 5), "3W"), 0.998459785)
        df_nzd_1M = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 2, 15), "1M"), 0.9978432525)
        df_nzd_2M = Rate.cls_discount_factor(nzd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 3, 15), "2M"), 0.9961389054)

        df_curve_nzd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_nzd_ON, df_nzd_TN, df_nzd_1W, df_nzd_2W, df_nzd_3W, df_nzd_1M,
                                                       df_nzd_2M],
                                                      Rate.linearization_enum.log_ds_factor)

        dv01 = PVBP.create_fx_forward_zcdv01_from_df_curves(test_trade, spot_rate_nzdusd, df_curve_usd, df_curve_nzd,date_of_today)

        # print(dv01.pvbp_d_pl_base_by_d_zc_base_f1)
        # print(dv01.pvbp_d_pl_base_by_d_zc_base_f2)
        #
        # print(dv01.pvbp_d_pl_base_by_d_zc_base_f3)
        # print(dv01.pvbp_d_pl_base_by_d_zc_base_f4)
        #
        #
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f1)
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f2)
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f2)
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f2)
        #
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f3)
        # print(dv01.pvbp_d_pl_und_by_d_zc_und_f4)

        # print(dv01.bucket_date3)
        # print(dv01.bucket_date4)

        self.assertEqual(round(dv01.pvbp_in_base_by_1bp_base,4), round(-187.681778,4))
        self.assertEqual(round(dv01.pvbp_in_und_by_1bp_und, 4), round(281.3547333, 4))
        self.assertEqual(round(dv01.pvbp_in_base_by_1bp_und, 4), round(192.0350207, 4))