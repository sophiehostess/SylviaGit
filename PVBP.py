#!/usr/bin/python
# -*- coding: utf-8 -*-

# Standard and third-party imports
import datetime
from log4py import logger
import Rate2 as Rate
import Trade as Trade

# Helper function to calculate interpolation fractions between bucket dates
def get_buckets_fractions(earlier_bucket_date:datetime.date, later_bucket_date:datetime.date, maturity_date:datetime.date)->tuple:
    """
    Calculates linear interpolation fractions between two bucket dates for a given maturity date
    Returns: (fraction for earlier bucket, fraction for later bucket)
    """
    if later_bucket_date != earlier_bucket_date:
        # Calculate proportional distance between bucket dates
        earlier_bucket_fraction = (later_bucket_date - maturity_date) / (later_bucket_date - earlier_bucket_date)
        later_bucket_fraction = (maturity_date - earlier_bucket_date) / (later_bucket_date - earlier_bucket_date)
    else:
        # Handle edge case where bucket dates are the same
        earlier_bucket_fraction = 1
        later_bucket_fraction = 0

    return (earlier_bucket_fraction, later_bucket_fraction)

class cls_fx_forward_zcdv01():
    """
    Class for calculating zero-curve DV01 (dollar value of 1 basis point) for FX forwards
    Handles sensitivity calculations for both base and underlying currencies
    """
    def __init__(self,
                 trade:Trade.cls_spot_forward_trade,          # The FX forward trade
                 df_base_t_s: Rate.cls_discount_factor,       # Discount factor for base currency at spot
                 df_base_t_m: Rate.cls_discount_factor,       # Discount factor for base currency at maturity
                 df_und_t_s: Rate.cls_discount_factor,        # Discount factor for underlying currency at spot
                 df_und_t_m: Rate.cls_discount_factor,        # Discount factor for underlying currency at maturity
                 spot_rate: Rate.cls_fx_spot_rate,            # FX spot rate
                 bucket_date1: datetime.date,                 # First bucket date for risk bucketing
                 bucket_date2: datetime.date,                 # Second bucket date
                 bucket_date3: datetime.date,                 # Third bucket date
                 bucket_date4: datetime.date,                 # Fourth bucket date
                 pl_cal_date:datetime.date                    # P&L calculation date
                 ):
        # Store input parameters
        self.pl_cal_date = pl_cal_date
        self.trade = trade
        
        # Store discount factors
        self.df_base_t_s = df_base_t_s
        self.df_base_t_m = df_base_t_m
        self.df_und_t_s = df_und_t_s
        self.df_und_t_m = df_und_t_m
        
        # Store bucket dates for risk interpolation
        self.bucket_date1 = bucket_date1
        self.bucket_date2 = bucket_date2
        self.bucket_date3 = bucket_date3
        self.bucket_date4 = bucket_date4
        
        # Convert spot rate to base/underlying quotation mode
        self.spot_rate = spot_rate.get_fx_rate_by_quotation_mode(Rate.quotation_mode_enum.base_und)
        # Calculate discounted spot rate
        self.spot0 = self.spot_rate.get_discounted_spot_rate(df_base_t_s, df_und_t_s)
        
        # Calculate initial PVBP values
        self.refresh_zcdv01()

    # Properties to access trade and rate information
    @property
    def base_basis(self)->int:
        """Number of days in year for base currency"""
        return self.df_base_t_s.currency.number_of_days_1year

    @property
    def und_basis(self)->int:
        """Number of days in year for underlying currency"""
        return self.df_und_t_s.currency.number_of_days_1year

    @property
    def number_of_days_t_s(self)->int:
        """Number of days to spot date"""
        return self.df_base_t_s.tenor.number_of_days

    @property
    def number_of_days_t_m(self)->int:
        """Number of days to maturity"""
        return self.df_base_t_m.tenor.number_of_days

    @property
    def base_amount(self)->float:
        """Base currency notional amount"""
        return self.trade.base_ccy_notional

    @property
    def und_amount(self)->float:
        """Underlying currency notional amount"""
        return self.trade.und_ccy_notional

    @property
    def spot_date(self)->datetime.date:
        """Spot date of the trade"""
        return self.df_und_t_s.maturity_date

    @property
    def maturity_date(self)->datetime.date:
        """Maturity date of the trade"""
        return self.df_und_t_m.maturity_date

    # Private methods for PVBP calculations
    def __get_d_pl_base_d_zc_base_t_s(self)->float:
        """Calculate derivative of P&L with respect to base currency zero curve at spot"""
        return -1 * self.und_amount * self.df_und_t_m.value / self.spot_rate.value / self.df_und_t_s.value * self.df_base_t_s.value**2 * self.number_of_days_t_s / self.base_basis

    def __get_d_pl_base_d_zc_base_t_m(self)->float:
        """Calculate derivative of P&L with respect to base currency zero curve at maturity"""
        return -1 * self.base_amount * self.df_base_t_m.value**2 * self.number_of_days_t_m / self.base_basis

    def __get_d_pl_und_by_d_zc_und_t_s(self)->float:
        """Calculate derivative of P&L with respect to underlying currency zero curve at spot"""
        return self.und_amount * self.df_und_t_m.value * self.number_of_days_t_s / self.und_basis * self.df_und_t_s.value

    def __get_d_pl_und_d_zc_und_t_m(self)->float:
        """Calculate derivative of P&L with respect to underlying currency zero curve at maturity"""
        return -1 * self.und_amount * self.df_und_t_m.value**2 * self.number_of_days_t_m / self.und_basis

# Factory functions for creating ZCDV01 objects

def create_fx_forward_zcdv01_from_df_curves(trade: Trade.cls_spot_forward_trade,
                                            spot_rate_input: Rate.cls_fx_spot_rate,
                                            pnl_ccy_df_curve: Rate.cls_discount_factor_curve,
                                            risk_ccy_df_curve: Rate.cls_discount_factor_curve,
                                            pnl_cal_date: datetime.date
                                           )->cls_fx_forward_zcdv01:
    """
    Creates ZCDV01 object from discount factor curves
    """
    # Extract key dates
    maturity_date = trade.maturity_date
    spot_date = spot_rate_input.spot_date
    today_date = risk_ccy_df_curve.today_date

    # Get discount factors for P&L currency
    pnl_ccy_df_t_s = pnl_ccy_df_curve.get_discount_factor_by_start_maturity(today_date, spot_date)
    pnl_ccy_df_t_m = pnl_ccy_df_curve.get_discount_factor_by_start_maturity(today_date, maturity_date)

    # Get discount factors for risk currency
    risk_ccy_df_t_s = risk_ccy_df_curve.get_discount_factor_by_start_maturity(today_date, spot_date)
    risk_ccy_df_t_m = risk_ccy_df_curve.get_discount_factor_by_start_maturity(today_date, maturity_date)

    # Get bucket dates for risk interpolation
    bucket_date_before_spot, bucket_date_after_spot = risk_ccy_df_curve.get_neighbor_tenor_dates_by_maturity_date(spot_date)
    bucket_date_before_maturity, bucket_date_after_maturity = risk_ccy_df_curve.get_neighbor_tenor_dates_by_maturity_date(maturity_date)

    return cls_fx_forward_zcdv01(trade,
                                 pnl_ccy_df_t_s,
                                 pnl_ccy_df_t_m,
                                 risk_ccy_df_t_s,
                                 risk_ccy_df_t_m,
                                 spot_rate_input,
                                 bucket_date_before_spot,
                                 bucket_date_after_spot,
                                 bucket_date_before_maturity,
                                 bucket_date_after_maturity,
                                 pnl_cal_date
                                 )

def create_fx_forward_zcdv01_from_df_curve_dict(trade: Trade.cls_spot_forward_trade,
                                                spot_rate_input: Rate.cls_fx_spot_rate,
                                                pnl_ccy_label: str,
                                                df_curve_dict: Rate.cls_discount_factor_curve_dict,
                                                pnl_cal_date: datetime.date
                                               )->cls_fx_forward_zcdv01:
    """
    Creates ZCDV01 object from a dictionary of discount factor curves
    """
    # Get P&L currency curve
    pnl_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(pnl_ccy_label)

    # Determine risk currency curve based on P&L currency
    if pnl_ccy_label == trade.und_ccy_label:
        risk_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(trade.base_ccy_label)
    elif pnl_ccy_label == trade.base_ccy_label:
        risk_ccy_df_curve = df_curve_dict.get_curve_by_currency_label(trade.und_ccy_label)
    else:
        risk_ccy_df_curve = None

    return create_fx_forward_zcdv01_from_df_curves(trade, spot_rate_input, pnl_ccy_df_curve, risk_ccy_df_curve, pnl_cal_date)

def create_fx_forward_pnl_from_swap_point_panel(trade: Trade.cls_spot_forward_trade,
                                                pnl_ccy_label:str,
                                                swap_point_panel: Rate.cls_swap_point_panel,
                                                pnl_cal_date: datetime.date
                                               )->cls_fx_forward_zcdv01:
    """
    Creates ZCDV01 object from swap point panel
    """
    # Determine P&L and risk currency curves based on P&L currency label
    if pnl_ccy_label == swap_point_panel.base_currency_label:
        pnl_ccy_df_curve = swap_point_panel.df_curve_base_ccy
        risk_ccy_df_curve = swap_point_panel.df_curve_und_ccy
    elif pnl_ccy_label == swap_point_panel.und_currency_label:
        risk_ccy_df_curve = swap_point_panel.df_curve_base_ccy
        pnl_ccy_df_curve = swap_point_panel.df_curve_und_ccy
    else:
        risk_ccy_df_curve = None
        pnl_ccy_df_curve = None

    return create_fx_forward_zcdv01_from_df_curves(trade, swap_point_panel.spot_rate, pnl_ccy_df_curve, risk_ccy_df_curve, pnl_cal_date)