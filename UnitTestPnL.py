#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade
import PnL as PnL


class Test_cls_fx_trade_eco_pnl1(unittest.TestCase):
    
    def test_init(self):

        test_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
                                           counterparty = "ABC123",
                                           portfolio = "PORT789",
                                           trade_date = datetime.date(2017,1,17),
                                           maturity_date = datetime.date(2017,5,11),
                                           base_ccy_input = " USD",
                                           quotation_input = "eUR-USD ",
                                           ccy1_input = "USD",
                                           ccy1_notional = -1200,
                                           ccy2_input = "EUR",
                                           ccy2_notional = 1000)

        forward_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(datetime.date(2017, 1, 17), datetime.date(2017,5,11)),1.5)

        acc_pnl = PnL.cls_fx_trade_acc_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.base,
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(acc_pnl.pnl_ccy_label, "USD")
        self.assertEqual(acc_pnl.base_ccy_label, "USD")
        self.assertEqual(acc_pnl.und_ccy_label, "EUR")


        self.assertEqual(round(acc_pnl.acc_pnl,7),  round(1000 *(1.5 - 1.2),7))


        eco_pnl = PnL.cls_fx_trade_eco_pnl(test_trade,
                                           forward_rate,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.base, Rate.cls_tenor(datetime.date(2017, 1, 17), test_trade.maturity_date),0.998),
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(round(eco_pnl.eco_pnl,7),  round(1000 *(1.5 - 1.2),7)*0.998 )


class Test_cls_fx_trade_eco_pnl2(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 5, 11),
                                           base_ccy_input=" USD",
                                           quotation_input="eUR-USD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="EUR",
                                           ccy2_notional=1000)

        forward_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair,
                                                Rate.cls_tenor(datetime.date(2017, 1, 17), test_trade.maturity_date), 1.5)

        acc_pnl = PnL.cls_fx_trade_acc_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.underlying,
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(round(acc_pnl.acc_pnl, 7), round(-1200 *(1/1.5 - 1/1.2), 7))

        eco_pnl = PnL.cls_fx_trade_eco_pnl(test_trade,
                                           forward_rate,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.underlying,
                                                                    Rate.cls_tenor(datetime.date(2017, 1, 17), test_trade.maturity_date), 0.997),
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(round(eco_pnl.eco_pnl, 7), round(-1200 * (1/1.5 - 1/1.2), 7) * 0.997)



class Test_cls_nsp_acc_pnl(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 5, 11),
                                           base_ccy_input=" USD",
                                           quotation_input="eUR-USD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="EUR",
                                           ccy2_notional=1000)

        today_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(datetime.date(2017, 5, 10), test_trade.maturity_date), 1.5)

        acc_pnl = PnL.cls_nsp_acc_pnl(test_trade,
                                      today_rate,
                                      test_trade.contract_price.currency_pair.base,
                                      datetime.date(2017, 5, 10))

        self.assertEqual(round(acc_pnl.acc_pnl, 7), round(1000 *(1.5 - 1.2), 7))


class Test_cls_nsp_eco_pnl(unittest.TestCase):
    def test_init(self):
        USD= Rate.cls_currency("USD", 360)

        ON_RATE_USD1 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,1), datetime.date(2017,10,2), ""),0.001)
        ON_RATE_USD2 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,2), datetime.date(2017,10,4), ""),0.002)
        ON_RATE_USD3 = Rate.cls_overnight_funding_rate(USD, Rate.cls_tenor(datetime.date(2017,10,4), datetime.date(2017,10,9), ""),0.003)

        ON_RATE_USD_PANEL = Rate.cls_on_funding_rate_panel(USD,[ON_RATE_USD1, ON_RATE_USD2, ON_RATE_USD3])

        self.assertEqual(ON_RATE_USD_PANEL.list_start_date, ON_RATE_USD1.tenor.start_date)
        self.assertEqual(ON_RATE_USD_PANEL.list_end_date, ON_RATE_USD3.tenor.maturity_date)


        EUR = Rate.cls_currency("EUR", 365)
        ON_RATE_EUR1 = Rate.cls_overnight_funding_rate(EUR, Rate.cls_tenor(datetime.date(2017,10,1), datetime.date(2017,10,2), ""),0.006)
        ON_RATE_EUR2 = Rate.cls_overnight_funding_rate(EUR, Rate.cls_tenor(datetime.date(2017,10,2), datetime.date(2017,10,4), ""),0.007)
        ON_RATE_EUR3 = Rate.cls_overnight_funding_rate(EUR, Rate.cls_tenor(datetime.date(2017,10,4), datetime.date(2017,10,9), ""),0.008)

        ON_RATE_EUR_PANEL = Rate.cls_on_funding_rate_panel(EUR,[ON_RATE_EUR1, ON_RATE_EUR2, ON_RATE_EUR3])

        self.assertEqual(ON_RATE_EUR_PANEL.list_start_date, ON_RATE_EUR1.tenor.start_date)
        self.assertEqual(ON_RATE_EUR_PANEL.list_end_date, ON_RATE_EUR3.tenor.maturity_date)


        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 10, 3),
                                           base_ccy_input=" USD",
                                           quotation_input="eUR-USD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="EUR",
                                           ccy2_notional=1000)

        today_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(datetime.date(2017, 10, 8), test_trade.maturity_date), 1.5)

        eco_pnl = PnL.cls_nsp_eco_pnl(test_trade,
                                      today_rate,
                                      USD,
                                      datetime.date(2017, 10, 8),
                                      ON_RATE_USD_PANEL,
                                      ON_RATE_EUR_PANEL
                                     )

        self.assertEqual(round(eco_pnl.acc_pnl, 7), round(1000 *(1.5 - 1.2), 7))

        usd_cash_flow_financing = -1200 * ( 0.002 * 1 / 360 + 0.003 * 4 / 360)
        #print("usd_cash_flow_financing is " + str(usd_cash_flow_financing))
        #print("eco_pnl.get_pnl_ccy_financing is " + str(eco_pnl.get_pnl_ccy_financing))

        eur_cash_flow_financing = 1000 * (0.007 * 1 / 365 + 0.008 * 4 / 365)

        #print("eur_cash_flow_financing is " + str(eur_cash_flow_financing))
        #print("eco_pnl.get_counter_ccy_financing is " + str(eco_pnl.get_counter_ccy_financing))

        self.assertEqual(eco_pnl.eco_pnl, eco_pnl.acc_pnl + usd_cash_flow_financing + eur_cash_flow_financing * today_rate.mid)




class Test_create_trade_eco_pnl_by_today_value(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2018, 1, 17),
                                           maturity_date=datetime.date(2018, 5, 11),
                                           base_ccy_input=" USD",
                                           quotation_input="eUR-USD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="EUR",
                                           ccy2_notional=1000)

        discounted_spot_input = Rate.cls_fx_discounted_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(datetime.date(2018, 3, 2),datetime.date(2018, 3, 2)), 1.5)

        USD = Rate.cls_currency("USD", 360)
        EUR = Rate.cls_currency("EUR", 365)

        pnl_ccy_df_t_m = Rate.cls_discount_factor(USD, Rate.cls_tenor(datetime.date(2018, 3, 2),datetime.date(2018, 5, 11)), 0.997 )

        risk_ccy_df_t_m = Rate.cls_discount_factor(EUR, Rate.cls_tenor(datetime.date(2018, 3, 2), datetime.date(2018, 5, 11)), 1.002)

        eco_pnl = PnL.create_trade_eco_pnl_by_today_value(test_trade,
                                                          pnl_ccy_df_t_m,
                                                          risk_ccy_df_t_m,
                                                          discounted_spot_input,
                                                          datetime.date(2018, 3, 2)
                                                         )

        self.assertEqual(round(eco_pnl.eco_pnl, 7), round(1000 * 1.002 * 1.5  + (-1200) * 0.997, 7))



class Test_create_trade_eco_pnl_by_spot_value(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2018, 1, 17),
                                           maturity_date=datetime.date(2018, 5, 11),
                                           base_ccy_input=" USD",
                                           quotation_input="eUR-USD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="EUR",
                                           ccy2_notional=1000)

        spot_input = Rate.cls_fx_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(datetime.date(2018, 3, 2),datetime.date(2017, 3, 4)), 1.4)

        USD = Rate.cls_currency("USD", 360)
        EUR = Rate.cls_currency("EUR", 365)

        pnl_ccy_df_s_m = Rate.cls_discount_factor(USD, Rate.cls_tenor(datetime.date(2018, 3, 4),datetime.date(2018, 5, 11)), 0.9997 )

        pnl_ccy_df_t_m = Rate.cls_discount_factor(USD, Rate.cls_tenor(datetime.date(2018, 3, 2), datetime.date(2018, 5, 11)), 0.99)

        risk_ccy_df_s_m = Rate.cls_discount_factor(EUR, Rate.cls_tenor(datetime.date(2018, 3, 4), datetime.date(2018, 5, 11)), 1.003)

        eco_pnl = PnL.create_trade_eco_pnl_by_spot_value(test_trade,
                                                         pnl_ccy_df_s_m,
                                                         risk_ccy_df_s_m,
                                                         pnl_ccy_df_t_m,
                                                         spot_input,
                                                         datetime.date(2018, 3, 2)
                                                         )

        self.assertEqual(round(eco_pnl.eco_pnl, 7), round(1000 * (1.4 * 1.003 / 0.9997 - 1.2) * 0.99, 7))



class Test_create_trade_eco_pnl_from_df_curves(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 7, 25),
                                           base_ccy_input=" USD",
                                           quotation_input="USD-SGD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="SGD",
                                           ccy2_notional=2000)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        date_of_today = datetime.date(2017, 6, 13)

        df_usd_ON = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999968868900009)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999937738800022)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 16), "S/N"), 0.999907939100022)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"),  0.999727254200085)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 29), "2W"),  0.999512368799956)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"),  0.998942551320812)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"),  0.997910475099995)
        df_usd_3M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"),  0.996788096599609)
        df_usd_6M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.993355657098983)
        df_usd_9M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"),  0.989821542597184)
        df_usd_1Y = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"),  0.986029614300948)

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M,
                                                       df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_usd_20170725 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_usd_20170615 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_usd_20170725 is ",  df_usd_20170725.mid)

        #self.assertEqual(round(df_usd_20170725.mid, 9), round(0.998657734071825, 9))

        sgd_ccy = Rate.cls_currency("SGD", 365, Rate.date_shift_enum.D2)

        df_sgd_ON = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999985489497763)
        df_sgd_TN = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999970979621296)
        df_sgd_1W = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"),  0.99984358252256)
        df_sgd_1M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"),  0.999372474118876)
        df_sgd_2M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"),  0.998656691210744)
        df_sgd_3M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"),  0.997894307136919)
        df_sgd_6M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.995520369701573)
        df_sgd_9M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"),  0.992886023243647)
        df_sgd_1Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"),  0.989835750383861)
        df_sgd_2Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 6, 17), "2Y"),  0.975986362472653)

        df_curve_sgd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_sgd_ON, df_sgd_TN, df_sgd_1W, df_sgd_1M, df_sgd_2M, df_sgd_3M,
                                                       df_sgd_6M, df_sgd_9M, df_sgd_1Y, df_sgd_2Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_sgd_20170725 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_sgd_20170615 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_sgd_20170725 is ",  df_sgd_20170725.mid)

        #self.assertEqual(round(df_sgd_20170725.mid, 9), round(0.999174965538092, 9))

        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000)

        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)

        eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(test_trade,
                                                          spot_rate_usdsgd,
                                                          df_curve_usd,
                                                          df_curve_sgd,
                                                          date_of_today
                                                          )

        mkt_fwd = spot_rate_usdsgd.mid * (df_usd_20170725.mid/df_usd_20170615.mid) /(df_sgd_20170725.mid/ df_sgd_20170615.mid)
        self.assertEqual(round(eco_pnl.eco_pnl, 9), round(  2000 * ( 1/mkt_fwd -  1/(2000/1200) ) *  df_usd_20170725.mid  , 9))
        #print("eco_pnl={eco_pnl}".format(eco_pnl=eco_pnl.eco_pnl))

class Test_create_trade_eco_pnl_from_swap_point_panel(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 7, 25),
                                           base_ccy_input=" USD",
                                           quotation_input="USD-SGD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="SGD",
                                           ccy2_notional=2000)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        date_of_today = datetime.date(2017, 6, 13)

        df_usd_ON = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999968868900009)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999937738800022)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 16), "S/N"), 0.999907939100022)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"), 0.999727254200085)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 29), "2W"), 0.999512368799956)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"), 0.998942551320812)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"), 0.997910475099995)
        df_usd_3M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"), 0.996788096599609)
        df_usd_6M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.993355657098983)
        df_usd_9M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"), 0.989821542597184)
        df_usd_1Y = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"), 0.986029614300948)

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M,
                                                       df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_usd_20170725 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_usd_20170615 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_usd_20170725 is ",  df_usd_20170725.mid)

        # self.assertEqual(round(df_usd_20170725.mid, 9), round(0.998657734071825, 9))

        sgd_ccy = Rate.cls_currency("SGD", 365, Rate.date_shift_enum.D2)

        df_sgd_ON = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999985489497763)
        df_sgd_TN = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999970979621296)
        df_sgd_1W = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"), 0.99984358252256)
        df_sgd_1M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"), 0.999372474118876)
        df_sgd_2M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"), 0.998656691210744)
        df_sgd_3M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"), 0.997894307136919)
        df_sgd_6M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.995520369701573)
        df_sgd_9M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"), 0.992886023243647)
        df_sgd_1Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"), 0.989835750383861)
        df_sgd_2Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 6, 17), "2Y"), 0.975986362472653)

        df_curve_sgd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_sgd_ON, df_sgd_TN, df_sgd_1W, df_sgd_1M, df_sgd_2M, df_sgd_3M,
                                                       df_sgd_6M, df_sgd_9M, df_sgd_1Y, df_sgd_2Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_sgd_20170725 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_sgd_20170615 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_sgd_20170725 is ",  df_sgd_20170725.mid)

        # self.assertEqual(round(df_sgd_20170725.mid, 9), round(0.999174965538092, 9))

        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000)

        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)

        swap_point_panel_usdsgd = Rate.cls_swap_point_panel(usdsgd, spot_rate_usdsgd, df_curve_usd, df_curve_sgd,False)
        swap_point_panel_usdsgd.refresh_swap_point_list()

        eco_pnl = PnL.create_trade_eco_pnl_from_swap_point_panel(test_trade,
                                                                 'USD',
                                                                 swap_point_panel_usdsgd,
                                                                 date_of_today
                                                                )

        mkt_fwd = spot_rate_usdsgd.mid * (df_usd_20170725.mid / df_usd_20170615.mid) / (df_sgd_20170725.mid / df_sgd_20170615.mid)
        self.assertEqual(round(eco_pnl.eco_pnl, 9), round(2000 * (1 / mkt_fwd - 1 / (2000 / 1200)) * df_usd_20170725.mid, 9))


class Test_create_trade_eco_pnl_from_df_curve_dict(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade(trade_uti="TEST12345",
                                           counterparty="ABC123",
                                           portfolio="PORT789",
                                           trade_date=datetime.date(2017, 1, 17),
                                           maturity_date=datetime.date(2017, 7, 25),
                                           base_ccy_input=" USD",
                                           quotation_input="USD-SGD ",
                                           ccy1_input="USD",
                                           ccy1_notional=-1200,
                                           ccy2_input="SGD",
                                           ccy2_notional=2000)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        date_of_today = datetime.date(2017, 6, 13)

        df_usd_ON = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999968868900009)
        df_usd_TN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999937738800022)
        df_usd_SN = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 16), "S/N"), 0.999907939100022)
        df_usd_1W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"), 0.999727254200085)
        df_usd_2W = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 29), "2W"), 0.999512368799956)
        df_usd_1M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"), 0.998942551320812)
        df_usd_2M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"), 0.997910475099995)
        df_usd_3M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"), 0.996788096599609)
        df_usd_6M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.993355657098983)
        df_usd_9M = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"), 0.989821542597184)
        df_usd_1Y = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"), 0.986029614300948)

        df_curve_usd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_usd_ON, df_usd_TN, df_usd_SN, df_usd_1W, df_usd_2W, df_usd_1M,
                                                       df_usd_2M, df_usd_3M, df_usd_6M, df_usd_9M, df_usd_1Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_usd_20170725 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_usd_20170615 = df_curve_usd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_usd_20170725 is ",  df_usd_20170725.mid)

        # self.assertEqual(round(df_usd_20170725.mid, 9), round(0.998657734071825, 9))

        sgd_ccy = Rate.cls_currency("SGD", 365, Rate.date_shift_enum.D2)

        df_sgd_ON = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 14), "O/N"), 0.999985489497763)
        df_sgd_TN = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15), "T/N"), 0.999970979621296)
        df_sgd_1W = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 22), "1W"), 0.99984358252256)
        df_sgd_1M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 7, 17), "1M"), 0.999372474118876)
        df_sgd_2M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 8, 15), "2M"), 0.998656691210744)
        df_sgd_3M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 9, 15), "3M"), 0.997894307136919)
        df_sgd_6M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2017, 12, 15), "6M"), 0.995520369701573)
        df_sgd_9M = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 3, 15), "9M"), 0.992886023243647)
        df_sgd_1Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2018, 6, 15), "1Y"), 0.989835750383861)
        df_sgd_2Y = Rate.cls_discount_factor(sgd_ccy, Rate.cls_tenor(date_of_today, datetime.date(2019, 6, 17), "2Y"), 0.975986362472653)

        df_curve_sgd = Rate.cls_discount_factor_curve(usd_ccy,
                                                      [df_sgd_ON, df_sgd_TN, df_sgd_1W, df_sgd_1M, df_sgd_2M, df_sgd_3M,
                                                       df_sgd_6M, df_sgd_9M, df_sgd_1Y, df_sgd_2Y],
                                                      Rate.linearization_enum.log_ds_factor)

        df_sgd_20170725 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 7, 25))
        df_sgd_20170615 = df_curve_sgd.get_discount_factor_by_maturity_date(datetime.date(2017, 6, 15))
        # print("df_sgd_20170725 is ",  df_sgd_20170725.mid)

        # self.assertEqual(round(df_sgd_20170725.mid, 9), round(0.999174965538092, 9))

        usdsgd = Rate.cls_currency_pair(usd_ccy, sgd_ccy, Rate.quotation_mode_enum.base_und, 10000)

        spot_tenor = Rate.cls_tenor(date_of_today, datetime.date(2017, 6, 15))
        spot_rate_usdsgd = Rate.cls_fx_spot_rate(usdsgd, spot_tenor, 1.38375)


        df_rate_curve_dict = Rate.cls_discount_factor_curve_dict(date_of_today)
        df_rate_curve_dict.add_curve_to_dict('USD', df_curve_usd)
        df_rate_curve_dict.add_curve_to_dict('SGD', df_curve_sgd)

        eco_pnl = PnL.create_trade_eco_pnl_from_df_curve_dict(test_trade,
                                                              spot_rate_usdsgd,
                                                              'USD',
                                                              df_rate_curve_dict,
                                                              date_of_today
                                                             )

        mkt_fwd = spot_rate_usdsgd.mid * (df_usd_20170725.mid / df_usd_20170615.mid) / (df_sgd_20170725.mid / df_sgd_20170615.mid)
        self.assertEqual(round(eco_pnl.eco_pnl, 9), round(2000 * (1 / mkt_fwd - 1 / (2000 / 1200)) * df_usd_20170725.mid, 9))


class Test_cls_fx_trade_simulation_pnl1(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade_detail(trade_uti="TEST12345",
                                                  counterparty="ABC123",
                                                  portfolio="PORT789",
                                                  trade_date=datetime.date(2017, 1, 17),
                                                  maturity_date=datetime.date(2017, 11, 7),
                                                  base_ccy_input="USD",
                                                  quotation_input="USD-JPY",
                                                  ccy1_input="USD",
                                                  ccy1_notional=10000000,
                                                  ccy2_input="JPY",
                                                  ccy2_notional=-1025580000,
                                                  contract_spot_value=104.348)


        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        jpy_ccy = Rate.cls_currency("JPY", 360, Rate.date_shift_enum.D2)

        usdjpy_ccy_pair = Rate.cls_currency_pair(usd_ccy, jpy_ccy, Rate.quotation_mode_enum.base_und, 100)

        date_of_today = datetime.date(2017, 8, 28)

        spot_date = datetime.date(2017, 8, 30)

        maturity_date = datetime.date(2017, 11, 7)

        spot_rate = Rate.cls_fx_spot_rate(usdjpy_ccy_pair, Rate.cls_tenor(date_of_today, spot_date), 109.655)

        usd_df_s_m = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 0.99750604925953)

        jpy_df_s_m = Rate.cls_discount_factor(jpy_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1.00075847561013)

        usd_df_earlier_bucket_date_maturity = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(datetime.date(2017, 10, 30), maturity_date, "2M"), 0.999700321913332)

        usd_df_later_bucket_date_maturity = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(datetime.date(2017, 11, 30), maturity_date, "3M"), 1.0008620749957)

        sim_pnl = PnL.create_trade_simulation_pnl_by_spot_value(test_trade,
                                                                usd_df_s_m,
                                                                jpy_df_s_m,
                                                                spot_rate,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                usd_df_later_bucket_date_maturity,
                                                                date_of_today
                                                               )

        self.assertEqual(round(sim_pnl.market_forward_rate.value, 6),  round(109.2986255, 6))
        self.assertEqual(round(sim_pnl.total_pnl_discounted_to_spot, 4), round(615178.3402, 4))
        self.assertEqual(round(sim_pnl.spot_pnl_discounted_to_spot, 4), round(474484.0303, 4))
        self.assertEqual(round(sim_pnl.swap_pnl_discounted_to_maturity, 4), round(141046.0719, 4))
        self.assertEqual(round(sim_pnl.base_ccy_cashflow_discounted_to_spot, 4), round(9975060.4926, 4))
        self.assertEqual(round(sim_pnl.und_ccy_cashflow_discounted_to_spot, 4), round(-1026357877.4162, 4))

        self.assertEqual(round(sim_pnl.earlier_bucket_swap_pnl, 4), round(104615.7251, 4))
        self.assertEqual(round(sim_pnl.later_bucket_swap_pnl, 4), round(36430.3649, 4))



class Test_cls_fx_trade_simulation_pnl2(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade_detail(trade_uti="0025G70005228441",
                                                  counterparty="ABC123",
                                                  portfolio="PORT789",
                                                  trade_date=datetime.date(2017, 8, 18),
                                                  maturity_date=datetime.date(2017, 8, 18),
                                                  base_ccy_input="USD",
                                                  quotation_input="USD-JPY",
                                                  ccy1_input="USD",
                                                  ccy1_notional=-3000000,
                                                  ccy2_input="JPY",
                                                  ccy2_notional=331911000,
                                                  contract_spot_value=110.637)


        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        jpy_ccy = Rate.cls_currency("JPY", 360, Rate.date_shift_enum.D2)

        usdjpy_ccy_pair = Rate.cls_currency_pair(usd_ccy, jpy_ccy, Rate.quotation_mode_enum.base_und, 100)

        date_of_today = datetime.date(2017, 8, 18)

        spot_date = datetime.date(2017, 8, 22)

        maturity_date = datetime.date(2017, 8, 18)

        spot_rate = Rate.cls_fx_spot_rate(usdjpy_ccy_pair, Rate.cls_tenor(date_of_today, spot_date), 109.975)

        usd_df_s_m = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/0.999853058430741)

        jpy_df_s_m = Rate.cls_discount_factor(jpy_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/1.0000133750856)

        usd_df_earlier_bucket_date_maturity = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(maturity_date, maturity_date, "TDY"), 1)


        sim_pnl = PnL.create_trade_simulation_pnl_by_spot_value(test_trade,
                                                                usd_df_s_m,
                                                                jpy_df_s_m,
                                                                spot_rate,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                date_of_today
                                                               )

        self.assertEqual(round(sim_pnl.market_forward_rate.value, 6),  round(109.9926334152, 6))
        self.assertEqual(round(sim_pnl.total_pnl_discounted_to_spot, 4), round(17577.3939, 4))
        self.assertEqual(round(sim_pnl.spot_pnl_discounted_to_spot, 4), round(18061.3036, 4))
        self.assertEqual(round(sim_pnl.swap_pnl_discounted_to_maturity, 4), round(-483.8386, 4))
        self.assertEqual(round(sim_pnl.base_ccy_cashflow_discounted_to_spot, 4), round(-3000440.8895, 4))
        self.assertEqual(round(sim_pnl.und_ccy_cashflow_discounted_to_spot, 4), round(331906560.7213, 4))

        self.assertEqual(round(sim_pnl.earlier_bucket_swap_pnl, 4), round(-483.8386, 4))
        self.assertEqual(round(sim_pnl.later_bucket_swap_pnl, 4), round(0, 4))


class Test_cls_fx_trade_simulation_pnl3(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade_detail(trade_uti="0039J40023822350",
                                                  counterparty="ABC123",
                                                  portfolio="PORT789",
                                                  trade_date=datetime.date(2017, 8, 11),
                                                  maturity_date=datetime.date(2017, 8, 14),
                                                  base_ccy_input="USD",
                                                  quotation_input="EUR-USD",
                                                  ccy1_input="EUR",
                                                  ccy1_notional=-214101486.49,
                                                  ccy2_input="USD",
                                                  ccy2_notional=253086583.860505,
                                                  contract_spot_value=1.18215)


        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        eur_ccy = Rate.cls_currency("EUR", 360, Rate.date_shift_enum.D2)

        eurusd_ccy_pair = Rate.cls_currency_pair(usd_ccy, eur_ccy, Rate.quotation_mode_enum.und_base, 10000)

        date_of_today = datetime.date(2017, 8, 14)

        spot_date = datetime.date(2017, 8, 16)

        maturity_date = datetime.date(2017, 8, 14)

        spot_rate = Rate.cls_fx_spot_rate(eurusd_ccy_pair, Rate.cls_tenor(date_of_today, spot_date), 1.1783)

        usd_df_s_m = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/0.99993457205887)

        eur_df_s_m = Rate.cls_discount_factor(eur_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/1.00004787630355)

        usd_df_earlier_bucket_date_maturity = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(maturity_date, maturity_date, "TDY"), 1)


        sim_pnl = PnL.create_trade_simulation_pnl_by_spot_value(test_trade,
                                                                usd_df_s_m,
                                                                eur_df_s_m,
                                                                spot_rate,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                date_of_today
                                                               )

        self.assertEqual(round(sim_pnl.market_forward_rate.value, 6),  round(1/1.1781665, 6))
        self.assertEqual(round(sim_pnl.total_pnl_discounted_to_spot, 4), round(839439.8006, 4))
        self.assertEqual(round(sim_pnl.spot_pnl_discounted_to_spot, 4), round(810855.3819, 4))
        self.assertEqual(round(sim_pnl.swap_pnl_discounted_to_maturity, 3), round(28582.5484, 3))
        self.assertEqual(round(sim_pnl.base_ccy_cashflow_discounted_to_spot, 4), round(253103143.8781, 4))
        self.assertEqual(round(sim_pnl.und_ccy_cashflow_discounted_to_spot, 4), round(-214091236.5930, 4))

        self.assertEqual(round(sim_pnl.earlier_bucket_swap_pnl, 3), round(28582.5484, 3))
        self.assertEqual(round(sim_pnl.later_bucket_swap_pnl, 4), round(0, 4))




class Test_cls_fx_trade_simulation_pnl4(unittest.TestCase):
    def test_init(self):
        test_trade = Trade.create_fx_trade_detail(trade_uti="0039J40023822351",
                                                  counterparty="ABC123",
                                                  portfolio="PORT789",
                                                  trade_date=datetime.date(2017, 8, 11),
                                                  maturity_date=datetime.date(2017, 8, 15),
                                                  base_ccy_input="USD",
                                                  quotation_input="EUR-USD",
                                                  ccy1_input="EUR",
                                                  ccy1_notional=214101486.49,
                                                  ccy2_input="USD",
                                                  ccy2_notional=-253100072.254154,
                                                  contract_spot_value=1.18215)


        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)

        eur_ccy = Rate.cls_currency("EUR", 360, Rate.date_shift_enum.D2)

        eurusd_ccy_pair = Rate.cls_currency_pair(usd_ccy, eur_ccy, Rate.quotation_mode_enum.und_base, 10000)

        date_of_today = datetime.date(2017, 8, 14)

        spot_date = datetime.date(2017, 8, 16)

        maturity_date = datetime.date(2017, 8, 15)

        spot_rate = Rate.cls_fx_spot_rate(eurusd_ccy_pair, Rate.cls_tenor(date_of_today, spot_date), 1.1783)

        usd_df_s_m = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/0.999967286029433)

        eur_df_s_m = Rate.cls_discount_factor(eur_ccy, Rate.cls_tenor(spot_date, maturity_date, ""), 1/1.00002542210804)

        usd_df_earlier_bucket_date_maturity = Rate.cls_discount_factor(usd_ccy, Rate.cls_tenor(maturity_date, maturity_date, "TOM"), 1)


        sim_pnl = PnL.create_trade_simulation_pnl_by_spot_value(test_trade,
                                                                usd_df_s_m,
                                                                eur_df_s_m,
                                                                spot_rate,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                usd_df_earlier_bucket_date_maturity,
                                                                date_of_today
                                                               )

        self.assertEqual(round(sim_pnl.market_forward_rate.value, 6),  round(1/1.1782315, 6))
        self.assertEqual(round(sim_pnl.total_pnl_discounted_to_spot, 4), round(-838984.1213, 4))
        self.assertEqual(round(sim_pnl.spot_pnl_discounted_to_spot, 4), round(-824317.6897, 4))
        self.assertEqual(round(sim_pnl.swap_pnl_discounted_to_maturity, 3), round(-14665.9518, 3))
        self.assertEqual(round(sim_pnl.base_ccy_cashflow_discounted_to_spot, 4), round(-253108352.4333, 4))
        self.assertEqual(round(sim_pnl.und_ccy_cashflow_discounted_to_spot, 4), round(214096043.7172, 4))

        self.assertEqual(round(sim_pnl.earlier_bucket_swap_pnl, 3), round(-14665.9518, 3))
        self.assertEqual(round(sim_pnl.later_bucket_swap_pnl, 4), round(0, 4))


if __name__ == '__main__':
    unittest.main()

