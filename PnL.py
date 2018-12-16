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
        self.__pnl_value = 0.0
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
                 pnl_cal_date:datetime.date
                ):

        if pnl_ccy.label == trade.base_ccy_label :
            self.pnl_presented_in_base_or_und = Rate.base_or_und_enum.base
        elif pnl_ccy.label == trade.und_ccy_label :
            self.pnl_presented_in_base_or_und = Rate.base_or_und_enum.und

        self.trade = trade

        if market_forward_rate is not None:
            self.market_forward_rate = market_forward_rate.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)
        else:
            self.market_forward_rate = None

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
                 pnl_cal_date:datetime.date
                ):

        super().__init__(trade,market_forward_rate, pnl_ccy, pnl_cal_date)
        self.acc_pnl = 0.0
        self.refresh_acc_pnl()

    def __get_accounting_pnl_value(self)->float:

        #convert all rates to base_und quotation mode
        contract_price = self.trade.contract_price.get_deal_price_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            und_ccy_notional = self.trade.und_ccy_notional
            acc_pnl = und_ccy_notional * (1/self.market_forward_rate.mid - 1/contract_price.mid)

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            base_ccy_notional = self.trade.base_ccy_notional
            acc_pnl = base_ccy_notional * (self.market_forward_rate.mid - contract_price.mid)

        else:
            acc_pnl = 0.0

        self.acc_pnl = acc_pnl
        return acc_pnl


    def refresh_acc_pnl(self):
        self.pnl_value = self.__get_accounting_pnl_value()
        #logger.info("Accounting PnL is {acc_pnl}. ".format(acc_pnl=str(self.acc_pnl)))

    def refresh_pnl(self):
        self.refresh_acc_pnl()

class cls_fx_trade_eco_pnl(cls_fx_trade_acc_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy_df_t_m: Rate.cls_discount_factor,
                 pnl_cal_date:datetime.date
                ):
        pnl_ccy = pnl_ccy_df_t_m.currency
        super().__init__(trade,market_forward_rate, pnl_ccy, pnl_cal_date)

        if pnl_ccy.label == trade.base_ccy_label :
            self.base_ccy_df_t_m = pnl_ccy_df_t_m
        elif pnl_ccy.label == trade.und_ccy_label :
            self.und_ccy_df_t_m = pnl_ccy_df_t_m

        self.eco_pnl = 0.0
        self.refresh_eco_pnl()

    def __get_economic_pnl_value(self, acc_pnl:float)->float:
        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base:
            eco_pnl = acc_pnl * self.base_ccy_df_t_m.mid

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und:
            eco_pnl = acc_pnl * self.und_ccy_df_t_m.mid

        else:
            eco_pnl = 0.0

        return eco_pnl

    def refresh_eco_pnl(self):
        self.pnl_value = self.__get_economic_pnl_value(self.acc_pnl)
        self.eco_pnl = self.pnl_value
        #logger.info("Economic PnL is {eco_pnl}. ".format(eco_pnl=str(self.eco_pnl)))

    # override the parent one
    def refresh_pnl(self):
        super().refresh_acc_pnl()
        self.refresh_eco_pnl()

def create_trade_eco_pnl_by_today_value(trade: Trade.cls_fx_trade,
                                        pnl_ccy_df_t_m: Rate.cls_discount_factor,
                                        risk_ccy_df_t_m: Rate.cls_discount_factor,
                                        discounted_spot: Rate.cls_fx_discounted_spot_rate,
                                        pnl_cal_date: datetime.date
                                       )->cls_fx_trade_eco_pnl:

    forward_rate = Rate.cls_fx_forward_rate(trade.currency_pair, Rate.cls_tenor(pnl_cal_date, trade.maturity_date))

    base_ccy_df_t_m =None
    und_ccy_df_t_m = None
    if trade.base_ccy_label == pnl_ccy_df_t_m.currency_label and trade.und_ccy_label == risk_ccy_df_t_m.currency_label:
        base_ccy_df_t_m = pnl_ccy_df_t_m
        und_ccy_df_t_m = risk_ccy_df_t_m
    elif trade.und_ccy_label == pnl_ccy_df_t_m.currency_label and trade.base_ccy_label == risk_ccy_df_t_m.currency_label:
        base_ccy_df_t_m = risk_ccy_df_t_m
        und_ccy_df_t_m = pnl_ccy_df_t_m
    else:
        assert (
            "PnL currency {pnl_ccy_label} and Risk currency {risk_ccy_label} does not match base currency {base_ccy_label} nor underlying currency {und_ccy_label}".format(
                pnl_ccy_label=pnl_ccy_df_t_m.currency_label, risk_ccy_label=risk_ccy_df_t_m.currency_label, base_ccy_label=trade.base_ccy_label, und_ccy_label=trade.und_ccy_label))

    if (base_ccy_df_t_m is not None) and (und_ccy_df_t_m is not None):
        forward_rate.set_forward_rate_by_discounted_spot_and_df(discounted_spot, base_ccy_df_t_m, und_ccy_df_t_m)

        # print("discounted_spot: {discounted_spot}".format(discounted_spot=discounted_spot.mid))
        # print("base_ccy_df_t_m: {base_ccy_df_t_m}".format(base_ccy_df_t_m=base_ccy_df_t_m.mid))
        # print("und_ccy_df_t_m: {und_ccy_df_t_m}".format(und_ccy_df_t_m=und_ccy_df_t_m.mid))
        # print("forward_rate: {forward_rate}".format(forward_rate=forward_rate.mid))

        return cls_fx_trade_eco_pnl(trade, forward_rate,  pnl_ccy_df_t_m, pnl_cal_date)

    else:
        return None


def create_trade_eco_pnl_by_spot_value(trade: Trade.cls_fx_trade,
                                       pnl_ccy_df_s_m: Rate.cls_discount_factor,
                                       risk_ccy_df_s_m: Rate.cls_discount_factor,
                                       pnl_ccy_df_t_m: Rate.cls_discount_factor,
                                       spot_rate: Rate.cls_fx_spot_rate,
                                       pnl_cal_date: datetime.date
                                      )->cls_fx_trade_eco_pnl:

    forward_rate = Rate.cls_fx_forward_rate(trade.currency_pair, Rate.cls_tenor(pnl_cal_date, trade.maturity_date))

    base_ccy_df_s_m =None
    und_ccy_df_s_m = None
    if trade.base_ccy_label == pnl_ccy_df_s_m.currency_label and trade.und_ccy_label == risk_ccy_df_s_m.currency_label:
        base_ccy_df_s_m = pnl_ccy_df_s_m
        und_ccy_df_s_m = risk_ccy_df_s_m
    elif trade.und_ccy_label == pnl_ccy_df_t_m.currency_label and trade.base_ccy_label == risk_ccy_df_s_m.currency_label:
        base_ccy_df_s_m = risk_ccy_df_s_m
        und_ccy_df_s_m = pnl_ccy_df_s_m
    else:
        assert (
            "PnL currency {pnl_ccy_label} and Risk currency {risk_ccy_label} does not match base currency {base_ccy_label} nor underlying currency {und_ccy_label}".format(
                pnl_ccy_label=pnl_ccy_df_s_m.currency_label, risk_ccy_label=risk_ccy_df_s_m.currency_label, base_ccy_label=trade.base_ccy_label, und_ccy_label=trade.und_ccy_label))

    if (base_ccy_df_s_m is not None) and (und_ccy_df_s_m is not None):
        forward_rate.set_forward_rate_by_spot_and_df(spot_rate, base_ccy_df_s_m, und_ccy_df_s_m)

        # print("discounted_spot: {discounted_spot}".format(discounted_spot=spot_rate.mid))
        # print("base_ccy_df_t_m: {base_ccy_df_t_m}".format(base_ccy_df_t_m=spot_rate.mid))
        # print("base_ccy_df_s_m: {base_ccy_df_s_m}".format(base_ccy_df_s_m=base_ccy_df_s_m.mid))
        # print("und_ccy_df_s_m: {und_ccy_df_s_m}".format(und_ccy_df_s_m=und_ccy_df_s_m.mid))
        # print("forward_rate: {forward_rate}".format(forward_rate=forward_rate.mid))

        return cls_fx_trade_eco_pnl(trade, forward_rate, pnl_ccy_df_t_m, pnl_cal_date)

    else:
        return None


def create_trade_eco_pnl_from_df_curves(trade: Trade.cls_fx_trade,
                                        spot_rate_input: Rate.cls_fx_spot_rate,
                                        pnl_ccy_df_curve: Rate.cls_discount_factor_curve,
                                        risk_ccy_df_curve: Rate.cls_discount_factor_curve,
                                        pnl_cal_date: datetime.date
                                       )->cls_fx_trade_eco_pnl:

    maturity_date = trade.maturity_date
    spot_date = spot_rate_input.spot_date

    #pnl currency
    pnl_ccy_df_t_s = pnl_ccy_df_curve.get_discount_factor_by_maturity_date(spot_date)
    pnl_ccy_df_t_m = pnl_ccy_df_curve.get_discount_factor_by_maturity_date(maturity_date)

    pnl_ccy_df_s_m = pnl_ccy_df_t_m.get_remaining_df(pnl_ccy_df_t_s)

    #risk currency
    risk_ccy_df_t_s = risk_ccy_df_curve.get_discount_factor_by_maturity_date(spot_date)
    risk_ccy_df_t_m = risk_ccy_df_curve.get_discount_factor_by_maturity_date(maturity_date)

    risk_ccy_df_s_m = risk_ccy_df_t_m.get_remaining_df(risk_ccy_df_t_s)

    return create_trade_eco_pnl_by_spot_value(trade, pnl_ccy_df_s_m, risk_ccy_df_s_m, pnl_ccy_df_t_m, spot_rate_input, pnl_cal_date)


def create_trade_eco_pnl_from_swap_point_panel(trade: Trade.cls_fx_trade,
                                               pnl_ccy_label:str,
                                               swap_point_panel: Rate.cls_swap_point_panel,
                                               pnl_cal_date: datetime.date
                                              )->cls_fx_trade_eco_pnl:

    maturity_date = trade.maturity_date

    forward_rate = swap_point_panel.get_forwrd_rate_by_maturity(maturity_date)

    if pnl_ccy_label == swap_point_panel.base_currency_label:
        pnl_ccy_df_t_m = swap_point_panel.df_curve_base_ccy.get_discount_factor_by_maturity_date(maturity_date)

    elif pnl_ccy_label == swap_point_panel.und_currency_label:
        pnl_ccy_df_t_m = swap_point_panel.df_curve_und_ccy.get_discount_factor_by_maturity_date(maturity_date)
    else:
        pnl_ccy_df_t_m = None

    return cls_fx_trade_eco_pnl(trade, forward_rate, pnl_ccy_df_t_m, pnl_cal_date)


def create_trade_eco_pnl_from_df_curve_dict(trade: Trade.cls_fx_trade,
                                            spot_rate_input: Rate.cls_fx_spot_rate,
                                            pnl_ccy_label: str,
                                            df_curve_dict: Rate.cls_discount_factor_curve_dict,
                                            pnl_cal_date: datetime.date
                                           )->cls_fx_trade_eco_pnl:

    swap_point_panel = df_curve_dict.get_swap_point_panel_by_currency_pair(trade.currency_pair, spot_rate_input)

    return create_trade_eco_pnl_from_swap_point_panel(trade, pnl_ccy_label, swap_point_panel, pnl_cal_date)


class cls_fx_trade_simulation_pnl(cls_fx_trade_pnl):
    def __init__(self,
                 trade: Trade.cls_spot_forward_trade_detail,
                 market_forward_rate: Rate.cls_fx_forward_rate,
                 market_spot_rate: Rate.cls_fx_spot_rate,
                 pnl_ccy_df_s_m: Rate.cls_discount_factor,
                 risk_ccy_df_s_m: Rate.cls_discount_factor,
                 pl_ccy_df_earlier_bucket_date_maturity: Rate.cls_discount_factor,
                 pl_ccy_df_later_bucket_date_maturity: Rate.cls_discount_factor,
                 pnl_cal_date: datetime.date
                ):

        # maturity date discount to spot date
        pnl_ccy = pnl_ccy_df_s_m.currency
        super().__init__(trade, market_forward_rate, pnl_ccy, pnl_cal_date)
        self.trade = trade
        self.market_spot_rate = market_spot_rate.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        self.pl_ccy_df_earlier_bucket_date_maturity = pl_ccy_df_earlier_bucket_date_maturity
        self.pl_ccy_df_later_bucket_date_maturity = pl_ccy_df_later_bucket_date_maturity


        if pnl_ccy.label == trade.base_ccy_label :
            self.base_ccy_df_s_m = pnl_ccy_df_s_m
            self.und_ccy_df_s_m = risk_ccy_df_s_m
        elif pnl_ccy.label == trade.und_ccy_label :
            self.und_ccy_df_s_m = pnl_ccy_df_s_m
            self.base_ccy_df_s_m = risk_ccy_df_s_m

        # pl discounted to spot date
        self.total_pnl_discounted_to_spot = 0.0

        self.spot_pnl_discounted_to_spot = 0.0
        self.swap_pnl_discounted_to_maturity = 0.0
        self.earlier_bucket_swap_pnl = 0.0
        self.later_bucket_swap_pnl = 0.0

        self.base_ccy_cashflow_discounted_to_spot = 0
        self.und_ccy_cashflow_discounted_to_spot = 0
        self.swap_pnl_projected_to_neighbor_tenors = True

        self.refresh_pl_values()

    @property
    def earlier_bucket_date(self)->datetime.date:
        return self.pl_ccy_df_earlier_bucket_date_maturity.start_date

    @property
    def later_bucket_date(self) -> datetime.date:
        return self.pl_ccy_df_later_bucket_date_maturity.start_date


    def __get_simulation_pnl_values(self)->tuple:

        #convert all rates to base_und quotation mode
        contract_price_value = self.trade.contract_price.get_deal_price_by_quotation_mode(Rate.quotation_mode_enum.base_und).value
        contract_spot_price_value = self.trade.spot_price.get_deal_price_by_quotation_mode(Rate.quotation_mode_enum.base_und).value


        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            und_ccy_notional = self.trade.und_ccy_notional
            acc_pnl = und_ccy_notional * (1/self.market_forward_rate.mid - 1/contract_price_value)
            total_pnl_discounted_to_spot = acc_pnl * self.base_ccy_df_s_m.mid


            if self.trade.maturity_date >= self.market_spot_rate.maturity_date :
                spot_pnl_discounted_to_spot = self.trade.und_ccy_notional * (1/self.market_spot_rate.value - 1/contract_spot_price_value) * self.base_ccy_df_s_m.mid
            else:
                spot_pnl_discounted_to_spot = self.trade.und_ccy_notional * (1/self.market_spot_rate.value - 1/contract_price_value) * self.base_ccy_df_s_m.mid

            # discount to maturity date
            swap_pnl_discounted_to_maturity = (total_pnl_discounted_to_spot  - spot_pnl_discounted_to_spot) / self.base_ccy_df_s_m.mid


        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            base_ccy_notional = self.trade.base_ccy_notional
            acc_pnl = base_ccy_notional * (self.market_forward_rate.mid - contract_price_value)


            total_pnl_discounted_to_spot = acc_pnl * self.und_ccy_df_s_m.mid

            if self.trade.maturity_date >= self.market_spot_rate.maturity_date:
                spot_pnl_discounted_to_spot = self.trade.base_ccy_notional * (self.market_spot_rate.value - contract_spot_price_value) * self.und_ccy_df_s_m.mid
            else:
                spot_pnl_discounted_to_spot = self.trade.base_ccy_notional * (self.market_spot_rate.value - contract_price_value) * self.und_ccy_df_s_m.mid


            # discount to maturity date
            swap_pnl_discounted_to_maturity = (total_pnl_discounted_to_spot - spot_pnl_discounted_to_spot) / self.und_ccy_df_s_m.mid

        else:
            total_pnl_discounted_to_spot = 0.0
            spot_pnl_discounted_to_spot = 0.0
            swap_pnl_discounted_to_maturity = 0

        if self.later_bucket_date != self.earlier_bucket_date :
            earlier_bucket_fraction = (self.later_bucket_date - self.trade.maturity_date) / (self.later_bucket_date - self.earlier_bucket_date)
            #print("earlier_bucket_fraction", earlier_bucket_fraction)

            later_bucket_fraction = (self.trade.maturity_date - self.earlier_bucket_date) / (self.later_bucket_date - self.earlier_bucket_date)
            #print("later_bucket_fraction", later_bucket_fraction)

            # discounted to bucket date
            earlier_bucket_swap_pnl = swap_pnl_discounted_to_maturity * earlier_bucket_fraction * self.pl_ccy_df_earlier_bucket_date_maturity.value
            later_bucket_swap_pnl = swap_pnl_discounted_to_maturity * later_bucket_fraction * self.pl_ccy_df_later_bucket_date_maturity.value

            swap_pnl_projected_to_neighbor_tenors = True
        else:
            earlier_bucket_swap_pnl = swap_pnl_discounted_to_maturity
            later_bucket_swap_pnl = 0

            swap_pnl_projected_to_neighbor_tenors = False

        return (total_pnl_discounted_to_spot, spot_pnl_discounted_to_spot, swap_pnl_discounted_to_maturity, earlier_bucket_swap_pnl, later_bucket_swap_pnl, swap_pnl_projected_to_neighbor_tenors)


    def __get_discounted_cash_flows(self)->tuple:
        base_ccy_discounted_cashflow = self.trade.base_ccy_notional * self.base_ccy_df_s_m.value
        und_ccy_discounted_cashflow = self.trade.und_ccy_notional * self.und_ccy_df_s_m.value

        return (base_ccy_discounted_cashflow, und_ccy_discounted_cashflow)

    def refresh_pl_values(self):
        self.total_pnl_discounted_to_spot, self.spot_pnl_discounted_to_spot, self.swap_pnl_discounted_to_maturity, self.earlier_bucket_swap_pnl, self.later_bucket_swap_pnl, self.swap_pnl_projected_to_neighbor_tenors= self.__get_simulation_pnl_values()
        self.pnl_value = self.total_pnl_discounted_to_spot

        self.base_ccy_cashflow_discounted_to_spot, self.und_ccy_cashflow_discounted_to_spot = self.__get_discounted_cash_flows()


def create_trade_simulation_pnl_by_spot_value(trade: Trade.cls_spot_forward_trade_detail,
                                              pnl_ccy_df_s_m: Rate.cls_discount_factor,
                                              risk_ccy_df_s_m: Rate.cls_discount_factor,
                                              spot_rate: Rate.cls_fx_spot_rate,
                                              pl_ccy_df_earlier_bucket_date_maturity: Rate.cls_discount_factor,
                                              pl_ccy_df_later_bucket_date_maturity: Rate.cls_discount_factor,
                                              pnl_cal_date: datetime.date
                                             )->cls_fx_trade_simulation_pnl:

    base_ccy_df_s_m =None
    und_ccy_df_s_m = None
    if trade.base_ccy_label == pnl_ccy_df_s_m.currency_label and trade.und_ccy_label == risk_ccy_df_s_m.currency_label:
        base_ccy_df_s_m = pnl_ccy_df_s_m
        und_ccy_df_s_m = risk_ccy_df_s_m
    elif trade.und_ccy_label == pnl_ccy_df_s_m.currency_label and trade.base_ccy_label == risk_ccy_df_s_m.currency_label:
        base_ccy_df_s_m = risk_ccy_df_s_m
        und_ccy_df_s_m = pnl_ccy_df_s_m
    else:
        assert ("PnL currency {pnl_ccy_label} and Risk currency {risk_ccy_label} does not match base currency {base_ccy_label} nor underlying currency {und_ccy_label}".format(
                pnl_ccy_label=pnl_ccy_df_s_m.currency_label, risk_ccy_label=risk_ccy_df_s_m.currency_label, base_ccy_label=trade.base_ccy_label, und_ccy_label=trade.und_ccy_label))

    if (base_ccy_df_s_m is not None) and (und_ccy_df_s_m is not None):

        forward_rate = Rate.create_forward_rate_by_spot_and_df(trade.currency_pair, Rate.cls_tenor(pnl_cal_date, trade.maturity_date), spot_rate, base_ccy_df_s_m, und_ccy_df_s_m)

        return cls_fx_trade_simulation_pnl(trade, forward_rate, spot_rate, pnl_ccy_df_s_m, risk_ccy_df_s_m, pl_ccy_df_earlier_bucket_date_maturity, pl_ccy_df_later_bucket_date_maturity, pnl_cal_date)

    else:
        return None



def create_trade_simulation_pnl_from_df_curves(trade: Trade.cls_spot_forward_trade_detail,
                                               spot_rate_input: Rate.cls_fx_spot_rate,
                                               pnl_ccy_df_curve: Rate.cls_discount_factor_curve,
                                               risk_ccy_df_curve: Rate.cls_discount_factor_curve,
                                               pnl_cal_date: datetime.date
                                              )->cls_fx_trade_simulation_pnl:
    maturity_date = trade.maturity_date
    spot_date = spot_rate_input.spot_date

    #pnl currency
    pnl_ccy_df_s_m = pnl_ccy_df_curve.get_discount_factor_by_start_maturity(spot_date, maturity_date)

    #risk currency
    risk_ccy_df_s_m = risk_ccy_df_curve.get_discount_factor_by_start_maturity(spot_date, maturity_date)

    # the tenors follows risk currency
    earlier_bucket_date, later_bucket_date = risk_ccy_df_curve.get_neighbor_tenor_dates_by_maturity_date(maturity_date)

    pnl_ccy_df_earlier_bucket_date_maturity = pnl_ccy_df_curve.get_discount_factor_by_start_maturity(earlier_bucket_date, maturity_date)
    pnl_ccy_df_later_bucket_date_maturity = pnl_ccy_df_curve.get_discount_factor_by_start_maturity(later_bucket_date, maturity_date)

    return create_trade_simulation_pnl_by_spot_value(trade, pnl_ccy_df_s_m, risk_ccy_df_s_m, spot_rate_input, pnl_ccy_df_earlier_bucket_date_maturity, pnl_ccy_df_later_bucket_date_maturity, pnl_cal_date)



def create_trade_simulation_pnl_from_df_curve_dict(trade: Trade.cls_spot_forward_trade_detail,
                                                   spot_rate_input: Rate.cls_fx_spot_rate,
                                                   pnl_ccy_label: str,
                                                   df_curve_dict: Rate.cls_discount_factor_curve_dict,
                                                   pnl_cal_date: datetime.date
                                                  )->cls_fx_trade_simulation_pnl:

    pnl_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(pnl_ccy_label)

    if pnl_ccy_label == trade.und_ccy_label:
        risk_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(trade.base_ccy_label)
    elif pnl_ccy_label == trade.base_ccy_label:
        risk_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(trade.und_ccy_label)
    else:
        risk_ccy_df_curve = None

    return create_trade_simulation_pnl_from_df_curves(trade, spot_rate_input, pnl_ccy_df_curve, risk_ccy_df_curve, pnl_cal_date)



def create_trade_simulation_pnl_from_swap_point_panel(trade: Trade.cls_spot_forward_trade_detail,
                                                      pnl_ccy_label:str,
                                                      swap_point_panel: Rate.cls_swap_point_panel,
                                                      pnl_cal_date: datetime.date
                                                     )->cls_fx_trade_simulation_pnl:

    if pnl_ccy_label == swap_point_panel.base_currency_label:
        pnl_ccy_df_curve= swap_point_panel.df_curve_base_ccy
        risk_ccy_df_curve = swap_point_panel.df_curve_und_ccy

    elif pnl_ccy_label == swap_point_panel.und_currency_label:
        risk_ccy_df_curve= swap_point_panel.df_curve_base_ccy
        pnl_ccy_df_curve = swap_point_panel.df_curve_und_ccy
    else:
        risk_ccy_df_curve = None
        pnl_ccy_df_curve = None

    return create_trade_simulation_pnl_from_df_curves(trade, swap_point_panel.spot_rate, pnl_ccy_df_curve, risk_ccy_df_curve, pnl_cal_date)








class cls_nsp_acc_pnl(cls_fx_trade_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_today_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_cal_date:datetime.date
                 ):

        super().__init__(trade, None, pnl_ccy, pnl_cal_date)

        self.market_today_rate = market_today_rate.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        self.acc_pnl = 0.0
        self.refresh_acc_pnl()

    def __get_accounting_pnl_value(self)->float:

        #convert all rates to base_und quotation mode
        contract_price = self.trade.contract_price.get_deal_price_by_quotation_mode(Rate.quotation_mode_enum.base_und)

        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            und_ccy_notional = self.trade.und_ccy_notional
            acc_pnl = und_ccy_notional * (1/self.market_today_rate.mid - 1/contract_price.mid)

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            base_ccy_notional = self.trade.base_ccy_notional
            acc_pnl = base_ccy_notional * (self.market_today_rate.mid - contract_price.mid)

        else:
            acc_pnl = 0.0

        self.acc_pnl = acc_pnl
        return acc_pnl

    def refresh_acc_pnl(self):
        self.pnl_value = self.__get_accounting_pnl_value()
        #logger.info("Accounting PnL is {acc_pnl}. ".format(acc_pnl=str(self.acc_pnl)))



class cls_nsp_eco_pnl(cls_nsp_acc_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_today_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_cal_date:datetime.date,
                 pnl_ccy_on_funding_rate_panel:Rate.cls_on_funding_rate_panel,
                 counter_ccy_on_funding_rate_panel:Rate.cls_on_funding_rate_panel
                 ):
        super().__init__(trade, market_today_rate, pnl_ccy, pnl_cal_date)

        self.eco_pnl = 0.0

        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base:
            pnl_ccy_notional = self.trade.base_ccy_notional
            counter_ccy_notional = self.trade.und_ccy_notional
        else:
            pnl_ccy_notional = self.trade.und_ccy_notional
            counter_ccy_notional = self.trade.base_ccy_notional

        self.__pnl_ccy_financing = self.__get_single_cash_flow_financing(self.pnl_ccy.number_of_days_1year,
                                                                         pnl_ccy_notional,
                                                                         self.trade.maturity_date,
                                                                         self.pnl_cal_date,
                                                                         pnl_ccy_on_funding_rate_panel)

        self.__counter_ccy_financing = self.__get_single_cash_flow_financing(self.trade.contract_price.currency_pair.get_another_currency(self.pnl_ccy).number_of_days_1year,
                                                                             counter_ccy_notional,
                                                                             self.trade.maturity_date,
                                                                             self.pnl_cal_date,
                                                                             counter_ccy_on_funding_rate_panel)

        self.refresh_eco_pnl()

    def __get_single_cash_flow_financing(self,
                                         number_of_days_1year:int,
                                         notional:float,
                                         start_date:datetime.date,
                                         end_date:datetime.date,
                                         on_funding_rate_panel:Rate.cls_on_funding_rate_panel)->float:

        on_funding_rate_dict = on_funding_rate_panel.get_on_rate_dict_by_start_end_date(start_date, end_date)
        result = 0
        for start_date_iter, on_funding_rate_iter in on_funding_rate_dict.items():
            financing_iter = notional * on_funding_rate_iter.mid * on_funding_rate_iter.tenor.number_of_days / number_of_days_1year
            result = result + financing_iter

        return result

    def __get_economic_pnl_value(self) -> float:
        if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base :
            self.__counter_ccy_financing_in_pnl_ccy = self.__counter_ccy_financing * (1/self.market_today_rate.mid)

        elif self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.und :
            self.__counter_ccy_financing_in_pnl_ccy = self.__counter_ccy_financing * self.market_today_rate.mid

        else:
            self.__counter_ccy_financing_in_pnl_ccy = 0

        eco_pnl = self.acc_pnl + self.__pnl_ccy_financing + self.__counter_ccy_financing_in_pnl_ccy
        self.eco_pnl = eco_pnl
        return eco_pnl

    def refresh_eco_pnl(self):
        self.pnl_value = self.__get_economic_pnl_value()

        #logger.info("Economic PnL is {eco_pnl}. ".format(eco_pnl=str(self.eco_pnl)))


    @property
    def get_pnl_ccy_financing(self)->float:
        return self.__pnl_ccy_financing


    @property
    def get_counter_ccy_financing(self)->float:
        return self.__counter_ccy_financing