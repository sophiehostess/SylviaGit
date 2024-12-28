#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Trade module for handling FX trading functionality.

This module provides classes and utilities for creating and managing FX trades,
including spot and forward trades. It handles trade creation, price calculations,
and trade details.

Classes:
    product_type_enum: Enumeration of supported FX product types
    cls_fx_trade: Base class for FX trades
    cls_spot_forward_trade: Class for spot and forward FX trades
    simple_cash_flow: Class representing a cash flow
    cls_spot_forward_trade_detail: Extended spot/forward trade with additional details

Functions:
    create_fx_trade: Factory function to create FX trades
    create_fx_trade_detail: Factory function to create detailed FX trades

Dependencies:
    - datetime: For date handling
    - log4py: For logging
    - Rate2: For FX rate and currency functionality
    - enum: For enumeration support
"""

import datetime
from log4py import logger
import Rate2 as Rate
from enum import Enum

class product_type_enum(Enum):
    """Enumeration of supported FX product types."""
    fx_spot_forward = "fx_spot_forward"
    fx_time_option = "fx_time_option"
    fx_ndf = "fx_ndf"


class cls_fx_trade:
    """
    Base class for FX trades.
    
    Represents a foreign exchange trade with core attributes and functionality.
    Handles trade identification, counterparty details, and price information.
    """
    
    def __init__(self,
                 trade_uti: str=None,
                 counterparty: str=None,
                 portfolio: str=None,
                 product_type: product_type_enum=None,
                 trade_date: datetime.date=None,
                 contract_price: Rate.cls_deal_price=None,
                 base_ccy_notional: float=None,
                 und_ccy_notional: float=None):
        """
        Initialize an FX trade.

        Args:
            trade_uti: Unique trade identifier
            counterparty: Trading counterparty identifier
            portfolio: Portfolio identifier
            product_type: Type of FX product
            trade_date: Date of trade execution
            contract_price: Price details of the trade
            base_ccy_notional: Notional amount in base currency
            und_ccy_notional: Notional amount in underlying currency
        """
        self.trade_uti = trade_uti
        self.counterparty = counterparty
        self.portfolio = portfolio
        self.product_type = product_type
        self.trade_date = trade_date
        self.contract_price = contract_price
        self.base_ccy_notional = base_ccy_notional
        self.und_ccy_notional = und_ccy_notional

    @property
    def base_ccy_label(self)->str:
        """Get the base currency label."""
        return self.contract_price.currency_pair.base.label

    @property
    def und_ccy_label(self)->str:
        """Get the underlying currency label."""
        return self.contract_price.currency_pair.underlying.label

    @property
    def maturity_date(self)->datetime.date:
        """Get the trade maturity date."""
        return self.contract_price.maturity_date

    @property
    def quotation_mode(self)->Rate.quotation_mode_enum:
        """Get the quotation mode of the currency pair."""
        return self.contract_price.currency_pair.quotation_mode

    @property
    def quotation(self)->str:
        """Get the currency pair quotation string."""
        return self.contract_price.currency_pair.quotation

    @property
    def get_reversed_price(self)->float:
        """Calculate the reversed price (1/price)."""
        return 1/self.contract_price.value

    @property
    def get_reversed_quotation_mode(self)->Rate.quotation_mode_enum:
        """Get the reversed quotation mode."""
        return Rate.quotation_mode_enum.base_und if self.quotation_mode == Rate.quotation_mode_enum.und_base else Rate.quotation_mode_enum.und_base

    @property
    def price(self)->float:
        """Get the trade price."""
        return self.contract_price.value

    @property
    def currency_pair(self)->Rate.cls_currency_pair:
        """Get the currency pair object."""
        return self.contract_price.currency_pair

    @property
    def currency_pair_label(self)->str:
        """Get the currency pair label."""
        return self.contract_price.currency_pair.label

class cls_spot_forward_trade(cls_fx_trade):
    """Class representing spot and forward FX trades."""
    
    def __init__(self,
                 trade_uti: str=None,
                 counterparty: str=None,
                 portfolio: str=None,
                 trade_date: datetime.date=None,
                 contract_price: Rate.cls_deal_price=None,
                 base_ccy_notional: float=None,
                 und_ccy_notional: float=None):
        """Initialize a spot/forward trade with FX trade attributes."""
        super().__init__(trade_uti, counterparty, portfolio, product_type_enum.fx_spot_forward, trade_date, contract_price, base_ccy_notional, und_ccy_notional)


def create_fx_trade(trade_uti: str=None,
                    counterparty: str=None,
                    portfolio: str=None,
                    trade_date: datetime.date=None,
                    maturity_date: datetime.date=None,
                    base_ccy_input: str=None,
                    quotation_input: str=None,
                    ccy1_input: str=None,
                    ccy1_notional: float=None,
                    ccy2_input: str=None,
                    ccy2_notional: float=None)->cls_spot_forward_trade:
    """
    Factory function to create an FX trade.
    
    Creates a spot/forward trade based on input parameters, handling currency pair
    creation and price calculations.

    Args:
        trade_uti: Unique trade identifier
        counterparty: Trading counterparty
        portfolio: Portfolio identifier
        trade_date: Trade execution date
        maturity_date: Trade maturity date
        base_ccy_input: Base currency code
        quotation_input: Currency pair quotation string
        ccy1_input: First currency code
        ccy1_notional: First currency notional amount
        ccy2_input: Second currency code
        ccy2_notional: Second currency notional amount

    Returns:
        cls_spot_forward_trade: Created trade object
    """
    ccy1 = ccy1_input.upper().strip()
    ccy2 = ccy2_input.upper().strip()
    base_ccy = base_ccy_input.upper().strip()
    quotation = quotation_input.upper().strip()

    ccy1_ = Rate.cls_currency(ccy1)
    ccy2_ = Rate.cls_currency(ccy2)

    if base_ccy == ccy1 :
        base_ccy_notional = ccy1_notional
        und_ccy_notional = ccy2_notional

        if quotation == Rate.build_quotation(ccy1, ccy2):
            ccy_pair = Rate.cls_currency_pair(ccy1_, ccy2_, Rate.quotation_mode_enum.base_und)
            fx_price = Rate.cls_deal_price(ccy_pair,maturity_date, abs(ccy2_notional/ccy1_notional))

        elif quotation == Rate.build_quotation(ccy2, ccy1):
            ccy_pair = Rate.cls_currency_pair(ccy1_, ccy2_, Rate.quotation_mode_enum.und_base)
            fx_price = Rate.cls_deal_price(ccy_pair, maturity_date, abs(ccy1_notional/ccy2_notional))

    elif base_ccy == ccy2 :
        base_ccy_notional = ccy2_notional
        und_ccy_notional = ccy1_notional

        if quotation == Rate.build_quotation(ccy1,ccy2):
            ccy_pair = Rate.cls_currency_pair(ccy2_, ccy1_, Rate.quotation_mode_enum.und_base)
            fx_price = Rate.cls_deal_price(ccy_pair, maturity_date, abs(ccy2_notional/ccy1_notional))

        elif quotation == Rate.build_quotation(ccy2, ccy1):
            ccy_pair = Rate.cls_currency_pair(ccy2_, ccy1_, Rate.quotation_mode_enum.base_und)
            fx_price = Rate.cls_deal_price(ccy_pair, maturity_date, abs(ccy1_notional/ccy2_notional))

    else:
        fx_price = None
        base_ccy_notional = None
        und_ccy_notional = None

    return cls_spot_forward_trade(trade_uti.upper().strip(),counterparty.upper().strip(), portfolio.upper().strip(), trade_date, fx_price, base_ccy_notional,und_ccy_notional)


class simple_cash_flow():
    """Class representing a simple cash flow with amount, date and currency."""
    
    def __init__(self,
                 amount:float,
                 payment_date:datetime.date,
                 currency:Rate.cls_currency,
                 ):
        """
        Initialize a cash flow.

        Args:
            amount: Cash flow amount
            payment_date: Date of payment
            currency: Currency of the cash flow
        """
        self.amount = amount
        self.payment_date = payment_date
        self.currency = currency


class cls_spot_forward_trade_detail(cls_spot_forward_trade):
    """Extended spot/forward trade class with additional price details."""
    
    def __init__(self,
                 trade_uti: str=None,
                 counterparty: str=None,
                 portfolio: str=None,
                 trade_date: datetime.date=None,
                 contract_price: Rate.cls_deal_price=None,
                 contract_spot_price: Rate.cls_deal_price = None,
                 base_ccy_notional: float=None,
                 und_ccy_notional: float=None):
        """
        Initialize a detailed spot/forward trade.

        Additional Args:
            contract_spot_price: Spot price at trade execution
        """
        super().__init__(trade_uti, counterparty, portfolio, trade_date, contract_price, base_ccy_notional, und_ccy_notional)

        self.spot_price = contract_spot_price
        self.swap_points_value = contract_price.value - contract_spot_price.value


def create_fx_trade_detail(trade_uti: str=None,
                           counterparty: str=None,
                           portfolio: str=None,
                           trade_date: datetime.date=None,
                           maturity_date: datetime.date=None,
                           base_ccy_input: str=None,
                           quotation_input: str=None,
                           ccy1_input: str=None,
                           ccy1_notional: float=None,
                           ccy2_input: str=None,
                           ccy2_notional: float=None,
                           contract_spot_value: float=None)->cls_spot_forward_trade_detail:
    """
    Factory function to create a detailed FX trade.
    
    Creates a detailed spot/forward trade with additional spot price information.

    Additional Args:
        contract_spot_value: Spot price value at trade execution

    Returns:
        cls_spot_forward_trade_detail: Created detailed trade object
    """
    fx_trade = create_fx_trade(trade_uti, counterparty, portfolio, trade_date, maturity_date, base_ccy_input, quotation_input, ccy1_input, ccy1_notional, ccy2_input, ccy2_notional)
    spot_price = Rate.cls_deal_price(fx_trade.currency_pair, fx_trade.maturity_date, contract_spot_value)

    return cls_spot_forward_trade_detail(fx_trade.trade_uti,
                                         fx_trade.counterparty,
                                         fx_trade.portfolio,
                                         fx_trade.trade_date,
                                         fx_trade.contract_price,
                                         spot_price,
                                         fx_trade.base_ccy_notional,
                                         fx_trade.und_ccy_notional
                                        )
