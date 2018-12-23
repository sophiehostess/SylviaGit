#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade
import PnL as PnL


class cls_fx_forward_pnl_explain():
    def __init__(self,
                 trade:Trade.cls_spot_forward_trade,
                 day1_date:datetime.date,
                 day1_spot_rate:Rate.cls_fx_spot_rate,
                 day1_base_ccy_market_quote_curve:Rate.cls_market_quote_curve,
                 day1_und_ccy_market_quote_curve:Rate.cls_market_quote_curve,
                 day2_date: datetime.date,
                 day2_spot_rate:Rate.cls_fx_spot_rate,
                 day2_base_ccy_market_quote_curve:Rate.cls_market_quote_curve,
                 day2_und_ccy_market_quote_curve:Rate.cls_market_quote_curve,
                 base_ccy_curve_basis:int=None,
                 und_ccy_curve_basis: int=None,
                 rate_curve_linearization:Rate.linearization_enum=Rate.linearization_enum.log_ds_factor
                 ):

        #pre-checking
        if trade.currency_pair.label != day1_spot_rate.currency_pair.label or \
           trade.currency_pair.label != day2_spot_rate.currency_pair.label or \
           day1_spot_rate.currency_pair.label != day2_spot_rate.currency_pair.label:
            assert("currency pair(s) does not match, trade is {trade_label}, day1_spot is {day1_spot_lable}, day2_spot is {day2_spot_label}".format(trade_label=trade.currency_pair.label ,day1_spot_lable=day1_spot_rate.currency_pair.label,day2_spot_label=day2_spot_rate.currency_pair.label  ))

        if day1_date == day2_date :
            assert("date of day1 and day2 can not be same, day1 is {day1_date}, day2 is {day2_date}".format(day1_date=day1_date.strftime("%Y-%m-%d"), day2_date=day2_date.strftime("%Y-%m-%d")))


        self.trade = trade

        self.day1_date = day1_date
        self.day2_date = day2_date

        day1_base_ccy_df_curve = day1_base_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day1_und_ccy_df_curve = day1_und_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)
        day2_base_ccy_df_curve = day2_base_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day2_und_ccy_df_curve = day2_und_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)

        self.day1_spot_rate = day1_spot_rate
        self.day2_spot_rate = day2_spot_rate

        self.day1_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                    self.day1_spot_rate,
                                                                    day1_base_ccy_df_curve,
                                                                    day1_und_ccy_df_curve,
                                                                    self.day1_date
                                                                    )

        day1_base_ccy_date_shifted_market_quote_curve = self.__create_date_shifted_market_quote_curve(day1_base_ccy_market_quote_curve, day2_base_ccy_market_quote_curve)
        day1_und_ccy_date_shifted_market_quote_curve = self.__create_date_shifted_market_quote_curve(day1_und_ccy_market_quote_curve, day2_und_ccy_market_quote_curve)

        day1_base_ccy_date_shifted_df_curve = day1_base_ccy_date_shifted_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day1_und_ccy_date_shifted_df_curve = day1_und_ccy_date_shifted_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)


        self.date_shifted_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                            Rate.cls_fx_spot_rate(self.day1_spot_rate.currency_pair, self.day2_spot_rate.tenor, self.day1_spot_rate.value, quotation_mode=self.day1_spot_rate.quotation_mode),
                                                                            day1_base_ccy_date_shifted_df_curve,
                                                                            day1_und_ccy_date_shifted_df_curve,
                                                                            self.day2_date
                                                                            )

        self.spot_rate_shifted_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                                 self.day2_spot_rate,
                                                                                 day1_base_ccy_date_shifted_df_curve,
                                                                                 day1_und_ccy_date_shifted_df_curve,
                                                                                 self.day2_date
                                                                                )

        self.day2_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                    self.day2_spot_rate,
                                                                    day2_base_ccy_df_curve,
                                                                    day2_und_ccy_df_curve,
                                                                    self.day2_date
                                                                    )


        eco_pnl_value_by_time_effect = self.date_shifted_eco_pnl.pnl_value - self.day1_eco_pnl.pnl_value

        eco_pnl_value_by_spot_rate_movement = self.spot_rate_shifted_eco_pnl.pnl_value - self.date_shifted_eco_pnl.pnl_value

        eco_pnl_value_by_yield_curve_movement = self.day2_eco_pnl.pnl_value - self.spot_rate_shifted_eco_pnl.pnl_value


        pnl_currency = day1_base_ccy_df_curve.currency
        self.eco_pnl_by_time_effect = PnL.cls_pnl(pnl_currency ,self.day2_date)
        self.eco_pnl_by_time_effect.pnl_value = eco_pnl_value_by_time_effect

        self.eco_pnl_by_spot_rate_movement = PnL.cls_pnl(pnl_currency, self.day2_date)
        self.eco_pnl_by_spot_rate_movement.pnl_value = eco_pnl_value_by_spot_rate_movement

        self.eco_pnl_by_yield_curve_movement = PnL.cls_pnl(pnl_currency, self.day2_date)
        self.eco_pnl_by_yield_curve_movement.pnl_value = eco_pnl_value_by_yield_curve_movement


    def __create_date_shifted_market_quote_curve(self,
                                                 day1_market_quote_curve,
                                                 day2_market_quote_curve,
                                                 )->Rate.cls_market_quote_curve:

        result_mq_curve = day1_market_quote_curve
        result_rate_list = []

        for day2_mq in day2_market_quote_curve.fx_rate_list:
            shifted_mq = day1_market_quote_curve.get_market_quote_by_label(day2_mq.label)
            shifted_mq.tenor = day2_mq.tenor

            result_rate_list.append(shifted_mq)

        result_mq_curve.fx_rate_list = result_rate_list

        return result_mq_curve

    @property
    def pnl_value_by_time(self)->float:
        return self.eco_pnl_by_time_effect.pnl_value

    @property
    def pnl_value_by_spot_rate(self)->float:
        return self.eco_pnl_by_spot_rate_movement.pnl_value

    @property
    def pnl_value_by_yield_curve(self)->float:
        return self.eco_pnl_by_yield_curve_movement.pnl_value

    @property
    def day1_pnl_value(self)->float:
        return self.day1_eco_pnl.pnl_value

    @property
    def day2_pnl_value(self)->float:
        return self.day2_eco_pnl.pnl_value

    @property
    def total_pl_movement_value(self)->float:
        return self.day2_pnl_value - self.day1_pnl_value









