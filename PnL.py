#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import math
import logging
import Rate2 as Rate
from enum import Enum
import Trade as Trade


class accounting_pnl():
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 spot_rate:Rate.cls_fx_spot_rate
                 ):
        pass

class economic_pnl(accounting_pnl):
    def __init__(self,
                 trade:Trade.cls_fx_trade,
                 market_forward_rate:Rate.cls_fx_forward_rate,
                 base_ccy_df_t_m: Rate.cls_discount_factor,
                 spot_rate:Rate.cls_fx_spot_rate
                 ):
        super().__init__(trade,market_forward_rate,spot_rate)
        pass


class nsp_pnl():
    pass


class cof():
    pass