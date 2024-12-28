"""
PnL (Profit and Loss) calculation module for financial trades.

This module provides classes and utilities for calculating and managing Profit and Loss
for various types of financial trades, with a specific focus on FX trades.

Classes:
    cls_pnl: Base class for PnL calculations
    cls_fx_trade_pnl: PnL calculator specific to FX trades

Dependencies:
    - Trade module: For trade-related classes
    - Rate module: For currency and rate-related functionality
    - datetime: For date handling
"""

# Standard library imports
import datetime

# Local application/library specific imports
import Trade
import Rate2 as Rate

class cls_pnl:
    """Base class for PnL calculations. Implementation details needed."""
    pass

class cls_fx_trade_pnl(cls_pnl):
    """
    A class to calculate and represent PnL (Profit and Loss) for FX trades.
    
    This class inherits from cls_pnl and handles PnL calculations specific to FX trades,
    taking into account base and underlying currencies.

    Attributes:
        pnl_presented_in_base_or_und: Enum indicating if PnL is in base or underlying currency
        trade: The FX trade object being analyzed
        market_forward_rate: The current market forward rate for the currency pair
        pnl_cal_date: The date for which PnL is being calculated
    """
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 pnl_ccy:Rate.cls_currency,
                 pnl_cal_date:datetime.date
                ):
        """
        Initialize the FX trade PnL calculator.

        Args:
            trade: FX trade object containing trade details
            market_forward_rate: Current market forward rate for the currency pair
            pnl_ccy: Currency in which to calculate PnL
            pnl_cal_date: Date for PnL calculation
        """
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
        """
        Get the currency label in which PnL is presented.

        Returns:
            str: Currency label (either base or underlying) used for PnL presentation
        """
        return self.trade.base_ccy_label if self.pnl_presented_in_base_or_und == Rate.base_or_und_enum.base else self.trade.und_ccy_label

    @property
    def base_ccy_label(self):
        """
        Get the base currency label of the trade.

        Returns:
            str: Base currency label
        """
        return self.trade.base_ccy_label

    @property
    def und_ccy_label(self):
        """
        Get the underlying currency label of the trade.

        Returns:
            str: Underlying currency label
        """
        return self.trade.und_ccy_label