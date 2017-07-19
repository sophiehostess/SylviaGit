#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime

import Rate2 as Rate
import Trade as Trade


if __name__ == '__main__':
    unittest.main()



class Test_cls_spot_forward_trade_1(unittest.TestCase):

    def test_init(self):

        result_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
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

        self.assertEqual(result_trade.trade_uti, "TEST12345")
        self.assertEqual(result_trade.counterparty, "ABC123")
        self.assertEqual(result_trade.portfolio, "PORT789")
        self.assertEqual(result_trade.base_ccy, "USD")
        self.assertEqual(result_trade.und_ccy, "EUR")
        self.assertEqual(result_trade.trade_date, datetime.date(2017,1,17))
        self.assertEqual(result_trade.maturity_date, datetime.date(2017,5,11))
        self.assertEqual(result_trade.quotation, "EUR-USD")
        self.assertEqual(result_trade.quotation_mode, Rate.quotation_mode_enum.und_base)
        self.assertEqual(result_trade.price, 1200/1000)


class Test_cls_spot_forward_trade_2(unittest.TestCase):

    def test_init(self):

        result_trade = Trade.create_fx_trade(trade_uti = "TEST12345",
                                             counterparty = "ABC123",
                                             portfolio = "PORT789",
                                             trade_date = datetime.date(2017,1,17),
                                             maturity_date = datetime.date(2017,5,11),
                                             base_ccy_input = " USD",
                                             quotation_input = "USD-cny ",
                                             ccy1_input = "CNY",
                                             ccy1_notional = -61000,
                                             ccy2_input = "USD",
                                             ccy2_notional = 10000)

        self.assertEqual(result_trade.trade_uti, "TEST12345")
        self.assertEqual(result_trade.counterparty, "ABC123")
        self.assertEqual(result_trade.portfolio, "PORT789")
        self.assertEqual(result_trade.base_ccy, "USD")
        self.assertEqual(result_trade.und_ccy, "CNY")
        self.assertEqual(result_trade.trade_date, datetime.date(2017,1,17))
        self.assertEqual(result_trade.maturity_date, datetime.date(2017,5,11))
        self.assertEqual(result_trade.quotation, "USD-CNY")
        self.assertEqual(result_trade.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(result_trade.price, 61000/10000)