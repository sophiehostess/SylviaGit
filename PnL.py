#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade


class cls_pnl():
    def __init__(self,
                 pnl_ccy:Rate.cls_currency,
                 pnl_cal_date:datetime.date
                 ):
        self.pnl_ccy = pnl_ccy
        self.__pnl_value = 0
        self.pnl_cal_date = pnl_cal_date

    @property
    def pnl_value(self)->float:
        return self.__pnl_value

    @pnl_value.setter
    def pnl_value(self, pnl_value_input:float):
        self.__pnl_value = pnl_value_input


class cls_fx_trade_pnl(cls_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_ccy_df_t_m: Rate.cls_discount_factor,
                 pnl_cal_date:datetime.date
                 ):

        if pnl_ccy.label == trade.base_ccy_label :
            self.pnl_presented_in_base_or_und = Rate.base_or_und_enum.base
            self.base_ccy_df_t_m = pnl_ccy_df_t_m
        elif pnl_ccy.label == trade.und_ccy_label :
            self.pnl_presented_in_base_or_und = Rate.base_or_und_enum.und
            self.und_ccy_df_t_m = pnl_ccy_df_t_m

        self.trade = trade

        self.market_forward_rate = market_forward_rate.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        self.pnl_cal_date = pnl_cal_date

        super().__init__(pnl_ccy,self.pnl_cal_date)

    @property
    def pnl_ccy_label(self):
        return self.trade.base_ccy_label if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base else self.trade.und_ccy_label

    @property
    def base_ccy_label(self):
        return self.trade.base_ccy_label

    @property
    def und_ccy_label(self):
        return self.trade.und_ccy_label


class cls_fx_trade_acc_pnl(cls_fx_trade_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_ccy_df_t_m: Rate.cls_discount_factor,
                 pnl_cal_date:datetime.date
                 ):

        super().__init__(trade,market_forward_rate, pnl_ccy, pnl_ccy_df_t_m, pnl_cal_date)
        self.acc_pnl = 0
        self.refresh_acc_pnl()

    def __get_accounting_pnl_value(self)->float:

        #convert all rates to base_und quotation mode
        contract_price = self.trade.contract_price.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            und_ccy_notional = self.trade.und_ccy_notional
            acc_pnl = und_ccy_notional * (1/self.market_forward_rate.mid - 1/contract_price.mid)

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            base_ccy_notional = self.trade.base_ccy_notional
            acc_pnl = base_ccy_notional * (self.market_forward_rate.mid - contract_price.mid)

        else:
            acc_pnl = 0

        self.acc_pnl = acc_pnl
        return acc_pnl


    def refresh_acc_pnl(self):
        self.pnl_value = self.__get_accounting_pnl_value()
        logger.info("Accounting PnL is {acc_pnl}. ".format(acc_pnl=str(self.acc_pnl)))

    def refresh_pnl(self):
        self.refresh_acc_pnl()

class cls_fx_trade_eco_pnl(cls_fx_trade_acc_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_ccy_df_t_m: Rate.cls_discount_factor,
                 pnl_cal_date:datetime.date
                 ):

        super().__init__(trade,market_forward_rate, pnl_ccy, pnl_ccy_df_t_m, pnl_cal_date)
        self.eco_pnl = 0
        self.refresh_eco_pnl()

    def __get_economic_pnl_value(self, acc_pnl:float)->float:
        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base:
            eco_pnl = acc_pnl * self.base_ccy_df_t_m.mid

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und:
            eco_pnl = acc_pnl * self.und_ccy_df_t_m.mid

        else:
            eco_pnl = 0

        return eco_pnl

    def refresh_eco_pnl(self):
        self.pnl_value = self.__get_economic_pnl_value(self.acc_pnl)
        self.eco_pnl = self.pnl_value
        logger.info("Economic PnL is {eco_pnl}. ".format(eco_pnl=str(self.eco_pnl)))

    def refresh_pnl(self):
        super().refresh_acc_pnl()
        self.refresh_eco_pnl()

    def calculate_eco_pnl_by_cash_flow(self,
                                       pnl_ccy_df_t_m: Rate.cls_discount_factor,
                                       risk_ccy_df_t_m: Rate.cls_discount_factor,
                                       discounted_spot_input: Rate.cls_fx_discounted_spot_rate
                                       )->float:

        discounted_spot = discounted_spot_input.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            self.eco_pnl = self.trade.base_ccy_notional * pnl_ccy_df_t_m + self.trade.und_ccy_notional * risk_ccy_df_t_m / discounted_spot.mid

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            self.eco_pnl = self.trade.und_ccy_notional * pnl_ccy_df_t_m + self.trade.base_ccy_notional * risk_ccy_df_t_m * discounted_spot.mid

        logger.info("Economic PnL is {eco_pnl}. ".format(eco_pnl=str(self.eco_pnl)))

        self.acc_pnl = self.eco_pnl / pnl_ccy_df_t_m
        logger.info("Accounting PnL is {acc_pnl}. ".format(acc_pnl=str(self.acc_pnl)))

        return self.eco_pnl


class cls_nsp_pnl():
    pass


class cls_cof():
    pass