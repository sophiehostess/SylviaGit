#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade
import PnL as PnL


if __name__ == '__main__':
    unittest.main()


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

        forward_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, test_trade.contract_price.tenor,1.5)

        acc_pnl = PnL.cls_fx_trade_acc_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.base,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.base, test_trade.contract_price.tenor,0.998),
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(acc_pnl.pnl_ccy_label, "USD")
        self.assertEqual(acc_pnl.base_ccy_label, "USD")
        self.assertEqual(acc_pnl.und_ccy_label, "EUR")


        self.assertEqual(round(acc_pnl.acc_pnl,7),  round(1000 *(1.5 - 1.2),7))


        eco_pnl = PnL.cls_fx_trade_eco_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.base,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.base, test_trade.contract_price.tenor,0.998),
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
                                                test_trade.contract_price.tenor, 1.5)

        acc_pnl = PnL.cls_fx_trade_acc_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.underlying,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.underlying,
                                                                    test_trade.contract_price.tenor, 0.997),
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(round(acc_pnl.acc_pnl, 7), round(-1200 *(1/1.5 - 1/1.2), 7))

        eco_pnl = PnL.cls_fx_trade_eco_pnl(test_trade,
                                           forward_rate,
                                           test_trade.contract_price.currency_pair.underlying,
                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.underlying,
                                                                    test_trade.contract_price.tenor, 0.997),
                                           datetime.date(2017, 1, 17)
                                           )

        self.assertEqual(round(eco_pnl.eco_pnl, 7), round(-1200 * (1/1.5 - 1/1.2), 7) * 0.997)