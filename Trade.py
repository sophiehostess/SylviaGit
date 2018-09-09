#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from log4py import logger
import Rate2 as Rate
from enum import Enum

class product_type_enum(Enum):
    fx_spot_forward = "fx_spot_forward"
    fx_time_option = "fx_time_option"
    fx_ndf = "fx_ndf"


class cls_fx_trade:
    def __init__(self,
                 trade_uti: str=None,
                 counterparty: str=None,
                 portfolio: str=None,
                 product_type: product_type_enum=None,
                 contract_price: Rate.cls_fx_rate=None,
                 base_ccy_notional: float=None,
                 und_ccy_notional: float=None):

        self.trade_uti = trade_uti
        self.counterparty = counterparty
        self.portfolio = portfolio
        self.product_type = product_type
        self.contract_price = contract_price
        self.base_ccy_notional = base_ccy_notional
        self.und_ccy_notional = und_ccy_notional

    @property
    def base_ccy_label(self)->str:
        return self.contract_price.currency_pair.base.label

    @property
    def und_ccy_label(self)->str:
        return self.contract_price.currency_pair.underlying.label

    @property
    def maturity_date(self)->datetime.date:
        return self.contract_price.tenor.maturity_date

    @property
    def trade_date(self)->datetime.date:
        return self.contract_price.tenor.start_date

    @property
    def quotation_mode(self)->Rate.quotation_mode_enum:
        return self.contract_price.currency_pair.quotation_mode

    @property
    def quotation(self)->str:
        return self.contract_price.currency_pair.quotation

    @property
    def get_reversed_price(self)->float:
        return 1/self.contract_price.mid

    @property
    def get_reversed_quotation_mode(self)->Rate.quotation_mode_enum:
        return Rate.quotation_mode_enum.base_und if self.quotation_mode == Rate.quotation_mode_enum.und_base else Rate.quotation_mode_enum.und_base

    @property
    def price(self)->float:
        return self.contract_price.mid

    @property
    def currency_pair(self)->Rate.cls_currency_pair:
        return self.contract_price.currency_pair



class cls_spot_forward_trade(cls_fx_trade):
    def __init__(self,
                 trade_uti: str=None,
                 counterparty: str=None,
                 portfolio: str=None,
                 contract_price: Rate.cls_fx_rate=None,
                 base_ccy_notional: float=None,
                 und_ccy_notional: float=None):
        super().__init__(trade_uti, counterparty, portfolio, product_type_enum.fx_spot_forward, contract_price, base_ccy_notional, und_ccy_notional)


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
    ccy1 = ccy1_input.upper().strip()
    ccy2 = ccy2_input.upper().strip()
    base_ccy = base_ccy_input.upper().strip()
    quotation = quotation_input.upper().strip()

    ccy1_ = Rate.cls_currency(ccy1)
    ccy2_ = Rate.cls_currency(ccy2)
    maturity = Rate.cls_tenor(trade_date,maturity_date)


    if base_ccy == ccy1 :

        base_ccy_notional = ccy1_notional
        und_ccy_notional = ccy2_notional

        if quotation == Rate.build_quotation(ccy1, ccy2):
            ccy_pair = Rate.cls_currency_pair(ccy1_, ccy2_, Rate.quotation_mode_enum.base_und)
            fx_price = Rate.cls_fx_rate(ccy_pair,maturity, abs(ccy2_notional/ccy1_notional))

        elif quotation == Rate.build_quotation(ccy2, ccy1):
            ccy_pair = Rate.cls_currency_pair(ccy1_, ccy2_, Rate.quotation_mode_enum.und_base)
            fx_price = Rate.cls_fx_rate(ccy_pair, maturity, abs(ccy1_notional/ccy2_notional))

    elif base_ccy == ccy2 :

        base_ccy_notional = ccy2_notional
        und_ccy_notional = ccy1_notional

        if quotation == Rate.build_quotation(ccy1,ccy2):
            ccy_pair = Rate.cls_currency_pair(ccy2_, ccy1_, Rate.quotation_mode_enum.und_base)
            fx_price = Rate.cls_fx_rate(ccy_pair, maturity, abs(ccy2_notional/ccy1_notional))

        elif quotation == Rate.build_quotation(ccy2, ccy1):
            ccy_pair = Rate.cls_currency_pair(ccy2_, ccy1_, Rate.quotation_mode_enum.base_und)
            fx_price = Rate.cls_fx_rate(ccy_pair, maturity, abs(ccy1_notional/ccy2_notional))

    logger.info(
        "contract price quotation_mode is {quotation_mode}. ".format(quotation_mode=str(ccy_pair.quotation_mode)))

    return cls_spot_forward_trade(trade_uti.upper().strip(),counterparty.upper().strip(), portfolio.upper().strip(),fx_price,base_ccy_notional,und_ccy_notional)


class simple_cash_flow():
    def __init__(self,
                 amount:float,
                 payment_date:datetime.date,
                 currency:Rate.cls_currency,
                 ):
        self.amount = amount
        self.payment_date = payment_date
