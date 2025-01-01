#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import datetime
import Rate2 as Rate
import Trade

class TestFXTrade(unittest.TestCase):
    """Test cases for FX trade creation and management"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Define common test data
        self.trade_date = datetime.date(2023, 1, 1)
        self.maturity_date = datetime.date(2023, 1, 3)
        self.trade_uti = "TEST123"
        self.counterparty = "CPTY1"
        self.portfolio = "PORT1"
        
        # Define currency amounts
        self.usd_amount = -1000000
        self.eur_amount = 925000

    def test_create_fx_trade_eurusd(self):
        """Test creation of EUR/USD trade"""
        trade = Trade.create_fx_trade(
            trade_uti=self.trade_uti,
            counterparty=self.counterparty,
            portfolio=self.portfolio,
            trade_date=self.trade_date,
            maturity_date=self.maturity_date,
            base_ccy_input="EUR",
            quotation_input="EUR-USD",
            ccy1_input="EUR",
            ccy1_notional=self.eur_amount,
            ccy2_input="USD",
            ccy2_notional=self.usd_amount
        )

        # Verify trade attributes
        self.assertEqual(trade.trade_uti, self.trade_uti.upper())
        self.assertEqual(trade.counterparty, self.counterparty.upper())
        self.assertEqual(trade.portfolio, self.portfolio.upper())
        self.assertEqual(trade.trade_date, self.trade_date)
        self.assertEqual(trade.maturity_date, self.maturity_date)
        self.assertEqual(trade.base_ccy_label, "EUR")
        self.assertEqual(trade.und_ccy_label, "USD")
        self.assertEqual(trade.base_ccy_notional, self.eur_amount)
        self.assertEqual(trade.und_ccy_notional, self.usd_amount)
        self.assertAlmostEqual(trade.price, abs(self.usd_amount/self.eur_amount))

    def test_create_fx_trade_detail(self):
        """Test creation of detailed FX trade with spot price"""
        spot_price = 1.0800
        trade_detail = Trade.create_fx_trade_detail(
            trade_uti=self.trade_uti,
            counterparty=self.counterparty,
            portfolio=self.portfolio,
            trade_date=self.trade_date,
            maturity_date=self.maturity_date,
            base_ccy_input="EUR",
            quotation_input="EUR-USD",
            ccy1_input="EUR",
            ccy1_notional=self.eur_amount,
            ccy2_input="USD",
            ccy2_notional=self.usd_amount,
            contract_spot_value=spot_price
        )

        # Verify detailed trade attributes
        self.assertEqual(trade_detail.spot_price.value, spot_price)
        self.assertAlmostEqual(
            trade_detail.swap_points_value, 
            trade_detail.price - spot_price
        )

    def test_quotation_modes(self):
        """Test different quotation modes for trades"""
        # Test EUR-USD quotation
        trade_eurusd = Trade.create_fx_trade(
            trade_uti=self.trade_uti,
            counterparty=self.counterparty,
            portfolio=self.portfolio,
            trade_date=self.trade_date,
            maturity_date=self.maturity_date,
            base_ccy_input="EUR",
            quotation_input="EUR-USD",
            ccy1_input="EUR",
            ccy1_notional=self.eur_amount,
            ccy2_input="USD",
            ccy2_notional=self.usd_amount
        )

        # Test USD-EUR quotation
        trade_usdeur = Trade.create_fx_trade(
            trade_uti=self.trade_uti,
            counterparty=self.counterparty,
            portfolio=self.portfolio,
            trade_date=self.trade_date,
            maturity_date=self.maturity_date,
            base_ccy_input="EUR",
            quotation_input="USD-EUR",
            ccy1_input="EUR",
            ccy1_notional=self.eur_amount,
            ccy2_input="USD",
            ccy2_notional=self.usd_amount
        )

        # Verify quotation modes and prices
        self.assertEqual(trade_eurusd.quotation_mode, Rate.quotation_mode_enum.base_und)
        self.assertEqual(trade_usdeur.quotation_mode, Rate.quotation_mode_enum.und_base)
        self.assertAlmostEqual(trade_eurusd.price * trade_usdeur.price, 1.0)

    def test_cash_flow(self):
        """Test cash flow creation"""
        amount = 1000000
        payment_date = datetime.date(2023, 1, 3)
        currency = Rate.cls_currency("USD")
        
        cash_flow = Trade.simple_cash_flow(amount, payment_date, currency)
        
        self.assertEqual(cash_flow.amount, amount)
        self.assertEqual(cash_flow.payment_date, payment_date)
        self.assertEqual(cash_flow.currency.label, "USD")

if __name__ == '__main__':
    unittest.main()
