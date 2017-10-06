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

        today_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, test_trade.contract_price.tenor, 1.5)

        acc_pnl = PnL.cls_nsp_acc_pnl(test_trade,
                                      today_rate,
                                      test_trade.contract_price.currency_pair.base,
                                      datetime.date(2017, 5, 10)
                                     )

        self.assertEqual(round(acc_pnl.acc_pnl, 7), round(1000 *(1.5 - 1.2), 7))

#        eco_pnl = PnL.cls_fx_trade_eco_pnl(test_trade,
#                                           forward_rate,
#                                           test_trade.contract_price.currency_pair.underlying,
#                                           Rate.cls_discount_factor(test_trade.contract_price.currency_pair.underlying,
#                                                                    test_trade.contract_price.tenor, 0.997),
#                                           datetime.date(2017, 1, 17)
#                                           )

        #self.assertEqual(round(eco_pnl.eco_pnl, 7), round(-1200 * (1/1.5 - 1/1.2), 7) * 0.997)




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

        today_rate = Rate.cls_fx_forward_rate(test_trade.contract_price.currency_pair, test_trade.contract_price.tenor, 1.5)

        eco_pnl = PnL.cls_nsp_eco_pnl(test_trade,
                                      today_rate,
                                      USD,
                                      datetime.date(2017, 10, 8),
                                      ON_RATE_USD_PANEL,
                                      ON_RATE_EUR_PANEL
                                     )

        self.assertEqual(round(eco_pnl.acc_pnl, 7), round(1000 *(1.5 - 1.2), 7))

        usd_cash_flow_financing = -1200 * ( 0.002 * 1 / 360 + 0.003 * 4 / 360)
        print("usd_cash_flow_financing is " + str(usd_cash_flow_financing))
        print("eco_pnl.get_pnl_ccy_financing is " + str(eco_pnl.get_pnl_ccy_financing))

        eur_cash_flow_financing = 1000 * (0.007 * 1 / 365 + 0.008 * 4 / 365)
        print("eur_cash_flow_financing is " + str(eur_cash_flow_financing))
        print("eco_pnl.get_counter_ccy_financing is " + str(eco_pnl.get_counter_ccy_financing))

        self.assertEqual(eco_pnl.eco_pnl, eco_pnl.acc_pnl + usd_cash_flow_financing + eur_cash_flow_financing * today_rate.mid)