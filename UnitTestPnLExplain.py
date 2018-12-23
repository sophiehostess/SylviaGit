#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade
import PnLExplain as PnLExplain


class Test_cls_fx_forward_pnl_explain1(unittest.TestCase):

    def test_init(self):

        test_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
                                           counterparty = "ABC123",
                                           portfolio = "PORT789",
                                           trade_date = datetime.date(2018,2,9),
                                           maturity_date = datetime.date(2018,3,2),
                                           base_ccy_input = "USD",
                                           quotation_input = "XAU-USD",
                                           ccy1_input = "XAU",
                                           ccy1_notional = -20000,
                                           ccy2_input = "USD",
                                           ccy2_notional = 26371900)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        xau_ccy = Rate.cls_currency("XAU", 360, Rate.date_shift_enum.D2)

        day1_date = datetime.date(2018, 2, 21)
        day1_spot_date = datetime.date(2018, 2, 23)

        day1_mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day1_date, datetime.date(2018,2,22), "O/N"), 1.610733665/100)
        day1_mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018,2,22), day1_spot_date, "T/N"), 1.610733727/100)
        day1_mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day1_spot_date, datetime.date(2018,2,26),"S/N"), 1.510544467/100)
        day1_mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day1_spot_date, datetime.date(2018,3,2), "1W"), 1.526565783/100)
        day1_mq_usd_curve = Rate.cls_market_quote_curve(usd_ccy, [day1_mq_usd_ON, day1_mq_usd_TN, day1_mq_usd_SN, day1_mq_usd_1W])


        day1_mq_xau_ON = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(day1_date, datetime.date(2018,2,22), "O/N"), -0.195261612/100)
        day1_mq_xau_TN = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(datetime.date(2018,2,22), day1_spot_date, "T/N"),  -0.195892557/100)
        day1_mq_xau_1W = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(day1_spot_date, datetime.date(2018,3,2), "1W"), -0.279873686/100)
        day1_mq_xau_curve = Rate.cls_market_quote_curve(xau_ccy, [day1_mq_xau_ON, day1_mq_xau_TN, day1_mq_xau_1W])

        day1_spot_rate = Rate.cls_fx_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(day1_date, day1_spot_date), 1326.875)


        day2_date = datetime.date(2018, 2, 22)
        day2_spot_date = datetime.date(2018, 2, 26)

        day2_mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day2_date, datetime.date(2018,2,23), "O/N"), 1.55864428/100)
        day2_mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018,2,23), day2_spot_date, "T/N"), 1.558709912/100)
        day2_mq_usd_SN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day2_spot_date, datetime.date(2018,2,27),"S/N"), 1.423044259/100)
        day2_mq_usd_1W = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day2_spot_date, datetime.date(2018,3,5), "1W"), 1.453172574/100)
        day2_mq_usd_curve = Rate.cls_market_quote_curve(usd_ccy, [day2_mq_usd_ON, day2_mq_usd_TN, day2_mq_usd_SN, day2_mq_usd_1W])


        day2_mq_xau_ON = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(day2_date, datetime.date(2018,2,23), "O/N"), -0.229904683/100)
        day2_mq_xau_TN = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(datetime.date(2018,2,23), day2_spot_date, "T/N"),  -0.2311340035/100)
        day2_mq_xau_1W = Rate.cls_market_quote(xau_ccy, Rate.cls_tenor(day2_spot_date, datetime.date(2018,3,5), "1W"), -0.336323647/100)
        day2_mq_xau_curve = Rate.cls_market_quote_curve(xau_ccy, [day2_mq_xau_ON, day2_mq_xau_TN, day2_mq_xau_1W])

        day2_spot_rate = Rate.cls_fx_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(day2_date, day2_spot_date), 1321.46)


        plexplain = PnLExplain.cls_fx_forward_pnl_explain(test_trade,
                                                          day1_date,
                                                          day1_spot_rate,
                                                          day1_mq_usd_curve,
                                                          day1_mq_xau_curve,
                                                          day2_date,
                                                          day2_spot_rate,
                                                          day2_mq_usd_curve,
                                                          day2_mq_xau_curve,
                                                          360,
                                                          360,
                                                          Rate.linearization_enum.log_ds_factor
                                                          )

        self.assertEqual(round(plexplain.day1_eco_pnl.pnl_value, 2), round(-174854.306721,2))
        self.assertEqual(round(plexplain.pnl_value_by_time, 2), round(3993.2903948,2))
        self.assertEqual(round(plexplain.pnl_value_by_spot_rate, 2), round(108283.9877, 2))
        self.assertEqual(round(plexplain.pnl_value_by_yield_curve, 2), round(53.9752, 2))
        self.assertEqual(round(plexplain.day2_eco_pnl.pnl_value, 2), round(-62523.05343, 2))
        self.assertEqual(round(plexplain.total_pl_movement_value, 2), round(112331.2533, 2))




class Test_cls_fx_forward_pnl_explain2(unittest.TestCase):

    def test_init(self):

        test_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
                                           counterparty = "ABC123",
                                           portfolio = "PORT789",
                                           trade_date = datetime.date(2018,8,3),
                                           maturity_date = datetime.date(2018,8,7),
                                           base_ccy_input = "USD",
                                           quotation_input = "USD-CHF",
                                           ccy1_input = "USD",
                                           ccy1_notional = -2500000000,
                                           ccy2_input = "CHF",
                                           ccy2_notional = 2487405250)

        usd_ccy = Rate.cls_currency("USD", 360, Rate.date_shift_enum.D2)
        chf_ccy = Rate.cls_currency("CHF", 360, Rate.date_shift_enum.D2)

        day1_date = datetime.date(2018, 8, 3)
        day1_spot_date = datetime.date(2018, 8, 7)

        day1_mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day1_date, datetime.date(2018,8,6), "O/N"), 1.875/100)
        day1_mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018,8,6), day1_spot_date, "T/N"), 2.374628964/100)
        day1_mq_usd_curve = Rate.cls_market_quote_curve(usd_ccy, [day1_mq_usd_ON, day1_mq_usd_TN,])


        day1_mq_chf_ON = Rate.cls_market_quote(chf_ccy, Rate.cls_tenor(day1_date, datetime.date(2018,2,22), "O/N"), -0.996906873/100)
        day1_mq_chf_TN = Rate.cls_market_quote(chf_ccy, Rate.cls_tenor(datetime.date(2018,2,22), day1_spot_date, "T/N"),  -0.471154971/100)
        day1_mq_chf_curve = Rate.cls_market_quote_curve(chf_ccy, [day1_mq_chf_ON, day1_mq_chf_TN])

        day1_spot_rate = Rate.cls_fx_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(day1_date, day1_spot_date), 0.99430)


        day2_date = datetime.date(2018, 8, 6)
        day2_spot_date = datetime.date(2018, 8, 8)

        day2_mq_usd_ON = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(day2_date, datetime.date(2018,8,7), "O/N"), 1.875/100)
        day2_mq_usd_TN = Rate.cls_market_quote(usd_ccy, Rate.cls_tenor(datetime.date(2018,8,7), day2_spot_date, "T/N"), 2.224884121/100)
        day2_mq_usd_curve = Rate.cls_market_quote_curve(usd_ccy, [day2_mq_usd_ON, day2_mq_usd_TN])


        day2_mq_chf_ON = Rate.cls_market_quote(chf_ccy, Rate.cls_tenor(day2_date, datetime.date(2018,8,7), "O/N"), -0.93720566904191/100)
        day2_mq_chf_TN = Rate.cls_market_quote(chf_ccy, Rate.cls_tenor(datetime.date(2018,8,7), day2_spot_date, "T/N"),  -0.605600164482862/100)
        day2_mq_chf_curve = Rate.cls_market_quote_curve(chf_ccy, [day2_mq_chf_ON, day2_mq_chf_TN])

        day2_spot_rate = Rate.cls_fx_spot_rate(test_trade.contract_price.currency_pair, Rate.cls_tenor(day2_date, day2_spot_date), 0.9984)


        plexplain = PnLExplain.cls_fx_forward_pnl_explain(test_trade,
                                                          day1_date,
                                                          day1_spot_rate,
                                                          day1_mq_usd_curve,
                                                          day1_mq_chf_curve,
                                                          day2_date,
                                                          day2_spot_rate,
                                                          day2_mq_usd_curve,
                                                          day2_mq_chf_curve,
                                                          360,
                                                          360,
                                                          Rate.linearization_enum.log_ds_factor
                                                          )

        self.assertEqual(round(plexplain.day1_eco_pnl.pnl_value, 2), round(1664369.15255854,2))
        #self.assertEqual(round(plexplain.pnl_value_by_time, 0), round(-197449.5135722,0))
        self.assertEqual(round(plexplain.pnl_value_by_spot_rate, 2), round(-10271915.6091309, 2))
        self.assertEqual(round(plexplain.pnl_value_by_yield_curve, 0), round(1058.408813, 0))
        self.assertEqual(round(plexplain.day2_eco_pnl.pnl_value, 2), round(-8803937.5613237, 2))
        self.assertEqual(round(plexplain.total_pl_movement_value, 2), round(-10468306.7138901, 2))
