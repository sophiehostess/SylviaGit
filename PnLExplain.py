#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import copy
import Rate2 as Rate
import Trade as Trade
import PnL as PnL


# Class to explain and break down PnL (Profit and Loss) movements for FX forward trades
# Decomposes PnL changes into three effects: time decay, spot rate movement, and yield curve movement
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
            assert("currency pair(s) does not match, trade is {trade_label}, day1_spot is {day1_spot_label}, day2_spot is {day2_spot_label}".format(trade_label=trade.currency_pair.label ,day1_spot_label=day1_spot_rate.currency_pair.label,day2_spot_label=day2_spot_rate.currency_pair.label  ))

        if day1_date == day2_date :
            assert("date of day1 and day2 can not be same, day1 is {day1_date}, day2 is {day2_date}".format(day1_date=day1_date.strftime("%Y-%m-%d"), day2_date=day2_date.strftime("%Y-%m-%d")))


        self.trade = trade

        self.day1_date = day1_date
        self.day2_date = day2_date

        # Convert market quote curves to discount factor curves for both currencies and days
        day1_base_ccy_df_curve = day1_base_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day1_und_ccy_df_curve = day1_und_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)
        day2_base_ccy_df_curve = day2_base_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day2_und_ccy_df_curve = day2_und_ccy_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)

        # Calculate Day 1 economic PnL using original rates and curves
        self.day1_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                    self.day1_spot_rate,
                                                                    day1_base_ccy_df_curve,
                                                                    day1_und_ccy_df_curve,
                                                                    self.day1_date
                                                                    )

        # Create date-shifted curves to isolate time effect
        day1_base_ccy_date_shifted_market_quote_curve = self.__create_date_shifted_market_quote_curve(day1_base_ccy_market_quote_curve, day2_base_ccy_market_quote_curve)
        day1_und_ccy_date_shifted_market_quote_curve = self.__create_date_shifted_market_quote_curve(day1_und_ccy_market_quote_curve, day2_und_ccy_market_quote_curve)

        day1_base_ccy_date_shifted_df_curve = day1_base_ccy_date_shifted_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, base_ccy_curve_basis)
        day1_und_ccy_date_shifted_df_curve = day1_und_ccy_date_shifted_market_quote_curve.get_discount_factor_curve(rate_curve_linearization, und_ccy_curve_basis)

        # Calculate PnL components:
        # 1. Date shifted PnL - shows effect of time decay only
        self.date_shifted_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                            Rate.cls_fx_spot_rate(self.day1_spot_rate.currency_pair, self.day2_spot_rate.tenor, self.day1_spot_rate.value, quotation_mode=self.day1_spot_rate.quotation_mode),
                                                                            day1_base_ccy_date_shifted_df_curve,
                                                                            day1_und_ccy_date_shifted_df_curve,
                                                                            self.day2_date
                                                                            )

        # 2. Spot rate shifted PnL - shows combined effect of time decay and spot rate movement
        self.spot_rate_shifted_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                                 self.day2_spot_rate,
                                                                                 day1_base_ccy_date_shifted_df_curve,
                                                                                 day1_und_ccy_date_shifted_df_curve,
                                                                                 self.day2_date
                                                                                )

        # 3. Day 2 PnL - shows total effect including yield curve changes
        self.day2_eco_pnl = PnL.create_trade_eco_pnl_from_df_curves(self.trade,
                                                                    self.day2_spot_rate,
                                                                    day2_base_ccy_df_curve,
                                                                    day2_und_ccy_df_curve,
                                                                    self.day2_date
                                                                    )

        # Calculate individual PnL effects
        eco_pnl_value_by_time_effect = self.date_shifted_eco_pnl.pnl_value - self.day1_eco_pnl.pnl_value
        eco_pnl_value_by_spot_rate_movement = self.spot_rate_shifted_eco_pnl.pnl_value - self.date_shifted_eco_pnl.pnl_value
        eco_pnl_value_by_yield_curve_movement = self.day2_eco_pnl.pnl_value - self.spot_rate_shifted_eco_pnl.pnl_value

        # Store PnL components in separate objects
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
        """
        Creates a new market quote curve that uses Day 1 rates but Day 2 tenors
        This helps isolate the effect of time decay in PnL calculations
        """
        # use deepcopy to ensure not affecting the original curve
        result_mq_curve = copy.deepcopy(day1_market_quote_curve)
        result_rate_list = []

        for day2_mq in day2_market_quote_curve.fx_rate_list:
            shifted_mq = day1_market_quote_curve.get_market_quote_by_label(day2_mq.label)
            shifted_mq.tenor = day2_mq.tenor

            result_rate_list.append(shifted_mq)

        result_mq_curve.fx_rate_list = result_rate_list

        return result_mq_curve

    @property
    def pnl_value_by_time(self)->float:
        """Returns PnL change due to time decay effect"""
        return self.eco_pnl_by_time_effect.pnl_value

    @property
    def pnl_value_by_spot_rate(self)->float:
        """Returns PnL change due to spot rate movements"""
        return self.eco_pnl_by_spot_rate_movement.pnl_value

    @property
    def pnl_value_by_yield_curve(self)->float:
        """Returns PnL change due to yield curve movements"""
        return self.eco_pnl_by_yield_curve_movement.pnl_value

    @property
    def day1_pnl_value(self)->float:
        return self.day1_eco_pnl.pnl_value

    @property
    def day2_pnl_value(self)->float:
        return self.day2_eco_pnl.pnl_value

    @property
    def total_pl_movement_value(self)->float:
        """Returns total PnL movement between Day 1 and Day 2"""
        return self.day2_pnl_value - self.day1_pnl_value









