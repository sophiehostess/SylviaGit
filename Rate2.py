
#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import math
from log4py import logger

from enum import Enum

def build_quotation(ccy1: str, ccy2: str):
    return ccy1 + "-" + ccy2


class quotation_mode_enum(Enum):
    base_und = "base-und"
    und_base = "und-base"


class linearization_enum(Enum):
    log_ds_factor = "log_ds_factor"
    linear_ds_rate = "linear_ds_rate"

class base_or_und_enum(Enum):
    base = "base"
    und = "und"

class discount_factor_methedology(Enum):
    lin_act_365 = "LIN ACT/365"
    lin_act_360 = "LIN ACT/360"
    exp_act_365 = "EXP ACT/365"

class tenor_label(Enum):
    ON = 100
    TN = 200
    SN = 300
    W1 = 400
    W2 = 500
    W3 = 600
    W4 = 700
    M1 = 800
    M2 = 900
    M3 = 1000
    M4 = 1100
    M5 = 1200
    M6 = 1300
    M7 = 1400
    M8 = 1500
    M9 = 1600
    M10 = 1700
    M11 = 1800
    Y1 = 1900
    M15 = 2000
    M18 = 2100
    M21 = 2200
    Y2 = 2300
    Y3 = 2400
    Y4 = 2500
    Y5 = 2600
    Y6 = 2700
    Y7 = 2800
    Y8 = 2900
    Y9 = 3000
    Y10 = 3100
    Y11 = 3200
    Y12 = 3300
    Y15 = 3400
    Y20 = 3500




class cls_currency:
    def __init__(self,
                 label: str=None,
                 number_of_days_1year: int=365):
        self.label = label.upper() if label is not None else label
        self.number_of_days_1year = number_of_days_1year


class cls_currency_pair:
    def __init__(self,
                 base: cls_currency,
                 underlying: cls_currency,
                 quotation_mode: quotation_mode_enum,
                 swap_point_factor: int=10000,
                 day_shift: int=2):
        self.base = base
        self.underlying = underlying

        self.quotation_mode = quotation_mode
        self.swap_point_factor = swap_point_factor

        self.day_shift = day_shift
        self.__quotation = ""

        if quotation_mode == quotation_mode_enum.base_und:
            self.__quotation = build_quotation(base.label, underlying.label)
        elif quotation_mode == quotation_mode_enum.und_base:
            self.__quotation = build_quotation(underlying.label, base.label)
        else:
            logger.critical("parameter quotation_mode {quotation_mode} is invalid".format(quotation_mode=quotation_mode.__repr__()))
            # ("quotation is " + self.__quotation)

    @property
    def quotation(self)->str:
        return self.__quotation

    def get_reversed_quotation_mode(self) -> quotation_mode_enum:
        if self.quotation_mode == quotation_mode_enum.base_und:
            quotation_mode = quotation_mode_enum.und_base
        elif self.quotation_mode == quotation_mode_enum.und_base:
            quotation_mode = quotation_mode_enum.base_und
        else:
            quotation_mode = quotation_mode_enum.und_base

        # print("quotation_mode is " + self.quotation_mode.__repr__())
        return quotation_mode

    def get_reversed_pair(self):
        return cls_currency_pair(self.base, self.underlying,
                                 self.get_reversed_quotation_mode(),
                                 self.swap_point_factor,
                                 self.day_shift)

    def get_another_currency(self,ccy1:cls_currency)->cls_currency:
        if ccy1.label == self.base.label:
            return self.underlying
        elif ccy1.label == self.underlying.label:
            return self.base

class cls_tenor:
    def __init__(self,
                 start_date: datetime.date,
                 maturity_date: datetime.date,
                 label: str=None):
        self.label = label.upper() if label is not None else label
        self.start_date = start_date
        self.maturity_date = maturity_date

        self.__number_of_days = (self.maturity_date - self.start_date).days

    @property
    def number_of_days(self)->int:
        return self.__number_of_days

    def get_inverse_tenor(self, label: str=None):
        return cls_tenor(self.maturity_date, self.start_date,
                         (self.label + " inverse").upper() if label is None else label)

        # print(self.start_date.strftime('%Y-%m-%d'))
        # print(self.maturity_date.strftime('%Y-%m-%d'))
        # print(self.number_of_days)

        # print(self.label + " " + str(self.start_date) + " " + str(self.maturity_date))


class cls_rate:
    def __init__(self,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.tenor = tenor
        self.__mid = 0.0
        self.__bid = 0.0
        self.__ask = 0.0
        self.__spread = 0.0

        if mid == 0 and bid != 0 and ask != 0:
            self.set_rate_by_bid_ask(bid, ask)
        else:
            self.__mid = mid
            if bid == 0 and ask == 0:
                self.set_rate_by_mid_spread(mid, 0)
            else:
                self.set_rate_by_bid_ask(bid, ask)

    def set_rate_by_bid_ask(self, bid: float, ask: float):
        self.__bid = bid
        self.__ask = ask
        self.__mid = (self.__bid + self.__ask) / 2
        self.__spread = abs(self.__bid - self.__mid)

    def set_rate_by_mid_bid_ask(self, mid: float, bid: float, ask: float):
        self.__mid = mid
        self.__bid = bid
        self.__ask = ask
        self.__spread = abs(self.__bid - self.__mid)

    def set_rate_by_mid_spread(self, mid: float, spread: float=None):
        self.__mid = mid

        if spread is not None:
            self.__spread = spread

        self.__bid = self.__mid - self.__spread
        self.__ask = self.__mid + self.__spread

    @property
    def mid(self)->float:
        return self.__mid

    @mid.setter
    def mid(self, mid):
        self.set_rate_by_mid_spread(mid, self.__spread)

    @property
    def bid(self)->float:
        return self.__bid

    @bid.setter
    def bid(self, bid):
        self.set_rate_by_bid_ask(bid, self.__ask)

    @property
    def ask(self)->float:
        return self.__ask

    @ask.setter
    def ask(self, ask):
        self.set_rate_by_bid_ask(self.__bid, ask)

    @property
    def spread(self)->float:
        return self.__spread

    @spread.setter
    def spread(self, spread):
        self.set_rate_by_mid_spread(self.__mid, spread)

    @property
    def value(self)->float:
        return self.__mid

    @value.setter
    def value(self, value):
        self.set_rate_by_mid_spread(value, self.__spread)

class cls_single_currency_rate(cls_rate):
    def __init__(self,
                 currency: cls_currency=None,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.currency = currency
        super().__init__(tenor, mid, bid, ask)
        self.__unique_key = self.__get_unique_key()

    def __get_unique_key(self)->str:
        return (self.__class__.__name__.replace("cls_","") + "#" +
                self.currency.label + "#" +
                self.tenor.start_date.strftime('%Y-%m-%d') + "#" +
                self.tenor.maturity_date.strftime('%Y-%m-%d'))

    @property
    def unique_key(self):
        return self.__unique_key

class cls_discount_factor(cls_single_currency_rate):
    def get_capitalized_factor(self):
        return cls_capitalized_factor(self.currency, self.tenor, 1 / self.mid)

    def get_discount_rate(self):
        return cls_discount_rate(
            self.currency, self.tenor, (1 / self.mid - 1) *
                                       self.currency.number_of_days_1year / self.tenor.number_of_days)

    def get_remaining_df(self, df1, label: str=None):

        # assume self = df1 * df2
        # get df2

        if self.tenor.start_date == df1.tenor.start_date:

            df2_tenor = cls_tenor(df1.tenor.maturity_date,
                                  self.tenor.maturity_date, label if label is not None else None)

            return cls_discount_factor(df1.currency, df2_tenor, self.mid / df1.mid)

        elif self.tenor.maturity_date == df1.tenor.maturity_date:

            df2_tenor = cls_tenor(self.tenor.start_date,
                                  df1.tenor.start_date, label if label is not None else None)

            return cls_discount_factor(df1.currency, df2_tenor, self.mid / df1.mid)

        else:
            logger.critical("parameter df1 tenor start data: %s maturity date: %s does not match current start date: %s maturity date: %s", df1.tenor.start_date, df1.tenor.maturity_date, self.tenor.start_date, self.tenor.maturity_date)
            return None

    def extend_by_df(self, df1, label: str=None):
        # assume df2 = self * df1
        # get df2

        if self.tenor.maturity_date == df1.tenor.start_date:

            df2_tenor = cls_tenor(self.tenor.start_date,
                                  df1.tenor.maturity_date, label if label is not None else None)

            return cls_discount_factor(self.currency, df2_tenor, self.mid * df1.mid)

        elif df1.tenor.maturity_date == self.tenor.start_date:

            df2_tenor = cls_tenor(df1.tenor.start_date,
                                  self.tenor.maturity_date, label if label is not None else None)

            return cls_discount_factor(self.currency, df2_tenor, df1.mid * self.mid)

        else:
            logger.critical("parameter df1 tenor start data: %s maturity date: %s does not match current start date: %s maturity date: %s", df1.tenor.start_date, df1.tenor.maturity_date, self.tenor.start_date, self.tenor.maturity_date)
            return None


class cls_capitalized_factor(cls_single_currency_rate):
    def get_discount_factor(self) -> cls_discount_factor:
        return cls_discount_factor(self.currency, self.tenor, 1 / self.mid)

    def get_discount_rate(self):
        return cls_discount_rate(
            self.currency, self.tenor, (self.mid - 1) * self.currency.number_of_days_1year / self.tenor.number_of_days)


class cls_market_quote(cls_single_currency_rate):
    def get_discount_rate(self,
                            discount_factor_today_spot: cls_discount_factor):

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_spot_to_maturity = self.tenor.number_of_days
            number_of_days_today_to_maturity = discount_factor_today_spot.tenor.number_of_days + number_of_days_spot_to_maturity

            ds_rate_value = self.currency.number_of_days_1year * (
                1 / discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_spot_to_maturity / self.currency.number_of_days_1year) - 1
            ) / number_of_days_today_to_maturity

            return cls_discount_rate(self.currency,
                                     cls_tenor(discount_factor_today_spot.tenor.start_date, self.tenor.maturity_date, self.tenor.label ),
                                     ds_rate_value)


        if self.tenor.maturity_date == discount_factor_today_spot.tenor.maturity_date:
            pass

        if self.tenor.maturity_date < discount_factor_today_spot.tenor.maturity_date:
            pass

    def get_discount_factor(self,
                            discount_factor_today_spot: cls_discount_factor):

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_spot_to_maturity = self.tenor.number_of_days

            ds_factor_value = discount_factor_today_spot.mid / (  1 + self.mid * number_of_days_spot_to_maturity / self.currency.number_of_days_1year)

            return cls_discount_factor(self.currency,
                                     cls_tenor(discount_factor_today_spot.tenor.start_date, self.tenor.maturity_date, self.tenor.label),
                                     ds_factor_value)

        if self.tenor.maturity_date == discount_factor_today_spot.tenor.maturity_date:
            pass

        if self.tenor.maturity_date < discount_factor_today_spot.tenor.maturity_date:
            pass

class cls_discount_rate(cls_single_currency_rate):
    def get_discount_factor(self):
        return cls_discount_factor(
            self.currency, self.tenor,
            1 / (1 + self.mid * self.tenor.number_of_days / self.currency.number_of_days_1year))

    def get_capitalized_factor(self):
        return cls_capitalized_factor(
            self.currency, self.tenor, 1 + self.mid * self.currency.number_of_days_1year / self.tenor.number_of_days)

    def get_market_quote(self, discount_factor_today_spot: cls_discount_factor
                         ) -> cls_market_quote:

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_today_to_maturity = self.tenor.number_of_days
            number_of_days_spot_to_maturity = number_of_days_today_to_maturity - discount_factor_today_spot.tenor.number_of_days

            market_quote_value = self.currency.number_of_days_1year * (
                discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_today_to_maturity / self.currency.number_of_days_1year) - 1
            ) / number_of_days_spot_to_maturity

            return cls_market_quote(
                self.currency,
                cls_tenor(discount_factor_today_spot.tenor.maturity_date,
                          self.tenor.maturity_date), market_quote_value)

        if self.tenor.maturity_date == discount_factor_today_spot.tenor.maturity_date:
            # T/N
            pass

        if self.tenor.maturity_date < discount_factor_today_spot.tenor.maturity_date:
            # O/N
            pass

class cls_overnight_funding_rate(cls_single_currency_rate):
    pass

class cls_on_funding_rate_panel():
    def __init__(
            self,
            currency: cls_currency,
            on_rate_list: list):
        if on_rate_list is not None:
            on_rate_list.sort(
                key=lambda on_rate: on_rate.tenor.start_date, reverse=False)
            self.on_rate_list = on_rate_list
        else:
            self.on_rate_list = []

        self.currency = currency

        self.__list_start_date = self.on_rate_list[0].tenor.start_date
        self.__list_end_date = self.on_rate_list[-1].tenor.maturity_date

    @property
    def list_start_date(self)->datetime.date:
        return self.__list_start_date

    @property
    def list_end_date(self)->datetime.date:
        return self.__list_end_date

    def get_on_rate_dict_by_start_end_date(
            self, start_date:datetime.date, end_date:datetime.date)->dict:

        result_dict = {}
        for on_rate_iter in self.on_rate_list:
            if on_rate_iter.tenor.start_date >= start_date and on_rate_iter.tenor.maturity_date <= end_date :
                result_dict[on_rate_iter.tenor.start_date] = on_rate_iter
                #print("add to dict , key is " + on_rate_iter.tenor.start_date.strftime('%Y-%m-%d') + " maturity is " + on_rate_iter.tenor.maturity_date.strftime('%Y-%m-%d'))

            if on_rate_iter.tenor.start_date < start_date and on_rate_iter.tenor.maturity_date <= end_date and on_rate_iter.tenor.maturity_date > start_date:
                result_dict[on_rate_iter.tenor.start_date] = cls_overnight_funding_rate(self.currency,
                                                                                        cls_tenor(start_date, on_rate_iter.tenor.maturity_date),
                                                                                        on_rate_iter.mid,
                                                                                        on_rate_iter.bid,
                                                                                        on_rate_iter.ask
                                                                                        )

            if on_rate_iter.tenor.start_date < start_date and on_rate_iter.tenor.maturity_date > end_date:
                result_dict[on_rate_iter.tenor.start_date] = cls_overnight_funding_rate(self.currency,
                                                                                        cls_tenor(start_date, end_date),
                                                                                        on_rate_iter.mid,
                                                                                        on_rate_iter.bid,
                                                                                        on_rate_iter.ask
                                                                                        )
                break
            elif on_rate_iter.tenor.start_date >= start_date and on_rate_iter.tenor.maturity_date > end_date :
                result_dict[on_rate_iter.tenor.start_date] = cls_overnight_funding_rate(self.currency,
                                                                                        cls_tenor(on_rate_iter.tenor.start_date, end_date),
                                                                                        on_rate_iter.mid,
                                                                                        on_rate_iter.bid,
                                                                                        on_rate_iter.ask
                                                                                        )
                #print("add to dict , key is " + on_rate_iter.tenor.start_date.strftime('%Y-%m-%d') + " maturity is " + end_date.strftime('%Y-%m-%d'))

                break
        return result_dict

class cls_currency_pair_rate(cls_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.currency_pair = currency_pair
        super().__init__(tenor, mid, bid, ask)
        self.__unique_key = self.__get_unique_key()

    def __get_unique_key(self)->str:
        return (self.__class__.__name__.replace("cls_","") + "#" +
                self.currency_pair.quotation + "#" +
                self.tenor.start_date.strftime('%Y-%m-%d') + "#" +
                self.tenor.maturity_date.strftime('%Y-%m-%d'))

    @property
    def unique_key(self):
        return self.__unique_key



class cls_fx_rate(cls_currency_pair_rate):
    def get_reversed_fx_rate(self):
        return cls_fx_rate(self.currency_pair.get_reversed_pair(), self.tenor,
                           1 / self.mid, 1 / self.bid, 1 / self.ask)

    def get_fx_rate_by_quotation_mode(self,
                                      quotation_mode: quotation_mode_enum):
        if quotation_mode == self.currency_pair.quotation_mode:
            return self
        else:
            return self.get_reversed_fx_rate()

    def get_fx_rate_by_quotation(self, quotation: str):
        if quotation == self.currency_pair.quotation:
            return self
        elif quotation == self.currency_pair.get_reversed_pair().quotation:
            return self.get_reversed_fx_rate()
        else:
            logger.critical("parameter quotation {quotation} is invalid".format(quotation=quotation))
            return None

    def init_by_cross_fx_rate(self, fx_rate_1, fx_rate_2):

        # Assume Maturity Date of fx_rate_1 and fx_rate_2 are the same

        fx1_base_und = fx_rate_1.get_fx_rate_by_quotation_mode(
            quotation_mode_enum.base_und)
        fx2_base_und = fx_rate_2.get_fx_rate_by_quotation_mode(
            quotation_mode_enum.base_und)

        if self.currency_pair.quotation == build_quotation(fx1_base_und.currency_pair.base.label, fx2_base_und.currency_pair.base.label) \
                and fx1_base_und.currency_pair.underlying.label == fx2_base_und.currency_pair.base.label:
            #EUR/USD GBP/USD --> EUR/GBP
            self.set_rate_by_bid_ask(fx1_base_und.bid / fx2_base_und.ask,
                                     fx1_base_und.ask / fx2_base_und.bid)

        elif self.currency_pair.quotation == build_quotation(fx1_base_und.currency_pair.base.label, fx2_base_und.currency_pair.underlying.label) \
                and fx1_base_und.currency_pair.underlying.label == fx2_base_und.currency_pair.base.label:
            # EUR/USD USD/HKD --> EUR/HKD
            self.set_rate_by_bid_ask(fx1_base_und.bid * fx2_base_und.bid,
                                     fx1_base_und.ask * fx2_base_und.ask)

        elif self.currency_pair.quotation == build_quotation(fx1_base_und.currency_pair.underlying.label, fx2_base_und.currency_pair.base.label) \
                and fx1_base_und.currency_pair.base.label == fx2_base_und.currency_pair.underlying.label:
            # USD/CAD AUD/USD --> CAD/AUD
            self.set_rate_by_bid_ask(1 / (fx1_base_und.ask * fx2_base_und.ask),
                                     1 / (fx1_base_und.bid * fx2_base_und.bid))

        elif self.currency_pair.quotation == build_quotation(fx1_base_und.currency_pair.underlying.label, fx2_base_und.currency_pair.underlying.label) \
                and fx1_base_und.currency_pair.base.label == fx2_base_und.currency_pair.base.label:
            # USD/HKD USD/JPY --> HKD/JPY
            self.set_rate_by_bid_ask(fx2_base_und.bid / fx1_base_und.ask,
                                     fx2_base_und.ask / fx1_base_und.bid)

        elif self.currency_pair.quotation == build_quotation(fx2_base_und.currency_pair.base.label, fx1_base_und.currency_pair.base.label) \
                and fx1_base_und.currency_pair.underlying.label == fx2_base_und.currency_pair.underlying.label:
            # GBP/USD EUR/USD --> EUR/GBP
            self.set_rate_by_bid_ask(fx2_base_und.bid / fx1_base_und.ask,
                                     fx2_base_und.ask / fx1_base_und.bid)

        elif self.currency_pair.quotation == build_quotation(fx2_base_und.currency_pair.base.label, fx1_base_und.currency_pair.underlying.label) \
                and fx1_base_und.currency_pair.base.label == fx2_base_und.currency_pair.underlying.label:
            # USD/HKD EUR/USD  --> EUR/HKD
            self.set_rate_by_bid_ask(fx1_base_und.bid * fx2_base_und.bid,
                                     fx1_base_und.ask * fx2_base_und.ask)

        elif self.currency_pair.quotation == build_quotation(fx2_base_und.currency_pair.underlying.label, fx1_base_und.currency_pair.base.label) \
                and fx1_base_und.currency_pair.underlying.label == fx2_base_und.currency_pair.base.label:
            # AUD/USD USD/CAD --> CAD/AUD
            self.set_rate_by_bid_ask(1 / (fx1_base_und.ask * fx2_base_und.ask),
                                     1 / (fx1_base_und.bid * fx2_base_und.bid))

        elif self.currency_pair.quotation == build_quotation(fx2_base_und.currency_pair.underlying.label, fx1_base_und.currency_pair.underlying.label) \
                and fx1_base_und.currency_pair.base.label == fx2_base_und.currency_pair.base.label:
            # USD/JPY USD/HKD --> HKD/JPY
            self.set_rate_by_bid_ask(fx1_base_und.ask / fx2_base_und.bid,
                                     fx1_base_und.bid / fx2_base_und.ask)


class cls_fx_spot_rate(cls_fx_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)
        self.tenor.label = "SPT"
        # print(str(self.mid))

    def get_spot_cls(self, fx_rate: cls_fx_rate):
        return cls_fx_spot_rate(fx_rate.currency_pair, fx_rate.tenor,
                                fx_rate.mid, fx_rate.bid, fx_rate.ask)

    def get_fx_rate_by_quotation(self, quotation: str):
        if quotation == self.currency_pair.quotation:
            return self
        elif quotation == self.currency_pair.get_reversed_pair().quotation:
            return self.get_spot_cls(self.get_reversed_fx_rate())
        else:
            logger.critical("parameter quotation {quotation}is invalid.".format(quotation=quotation))
            return None


class cls_fx_forward_rate(cls_fx_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)

        self.__spot_rate = cls_fx_spot_rate(currency_pair, tenor, mid, bid,
                                            ask)
        self.__swap_point = cls_swap_point(currency_pair, tenor, 0, 0, 0)

    @property
    def spot_rate(self)->cls_fx_spot_rate:
        return self.__spot_rate

    @spot_rate.setter
    def spot_rate(self, spot_rate_value: cls_rate):
        self.__spot_rate.set_rate_by_mid_bid_ask(
            spot_rate_value.mid, spot_rate_value.bid, spot_rate_value.ask)
        self.set_rate_by_mid_bid_ask(
            spot_rate_value.mid +
            self.__swap_point.mid / self.currency_pair.swap_point_factor,
            spot_rate_value.bid +
            self.__swap_point.bid / self.currency_pair.swap_point_factor,
            spot_rate_value.ask +
            self.__swap_point.ask / self.currency_pair.swap_point_factor)

    @property
    def swap_point(self):
        return self.__swap_point

    @swap_point.setter
    def swap_point(self, swap_point_value: cls_rate):
        self.set_rate_by_mid_bid_ask(
            swap_point_value.mid, swap_point_value.bid, swap_point_value.ask)

        self.set_rate_by_mid_bid_ask(
            self.__spot_rate.mid + swap_point_value.mid / self.currency_pair.swap_point_factor,
            self.__spot_rate.bid + swap_point_value.bid / self.currency_pair.swap_point_factor,
            self.__spot_rate.ask + swap_point_value.ask / self.currency_pair.swap_point_factor)

    def set_forward_rate_by_spot_and_df(
            self,
            spot_rate: cls_fx_spot_rate,
            base_ccy_df_s_m: cls_discount_factor,
            underlying_ccy_df_s_m: cls_discount_factor):

        spot_rate_with_aligned_quotation_mode = spot_rate.get_fx_rate_by_quotation_mode(
            self.currency_pair.quotation_mode)

        if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
            self.mid = self.currency_pair.swap_point_factor * spot_rate_with_aligned_quotation_mode.mid * (
                base_ccy_df_s_m.mid / underlying_ccy_df_s_m.mid - 1)
        elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
            self.mid = self.currency_pair.swap_point_factor * spot_rate_with_aligned_quotation_mode.mid * (
                underlying_ccy_df_s_m.mid / base_ccy_df_s_m.mid - 1)

    def set_forward_rate_by_spot_and_swp(self,
                                         spot_rate_value: cls_fx_spot_rate,
                                         swap_point_value: cls_rate):
        self.spot_rate = spot_rate_value
        self.swap_point = swap_point_value


class cls_fx_discounted_spot_rate(cls_fx_forward_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)
        self.tenor.label = "TDY"

class cls_swap_point(cls_fx_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)

    def set_swap_point_by_setting_forward_rate_and_spot(
            self, spot_rate: cls_fx_spot_rate,
            forward_rate: cls_fx_forward_rate):

        spot_rate_with_aligned_quotation_mode = spot_rate.get_fx_rate_by_quotation_mode(
            self.currency_pair.quotation_mode)
        forward_rate_with_aligned_quotation_mode = forward_rate.get_fx_rate_by_quotation_mode(
            self.currency_pair.quotation_mode)

        self.mid = (forward_rate_with_aligned_quotation_mode.mid -
                    spot_rate_with_aligned_quotation_mode.mid
                    ) * self.currency_pair.swap_point_factor

    def set_swap_point_by_discount_factor(
            self,
            spot_rate: cls_fx_spot_rate,
            df_base_s_m: cls_discount_factor,
            df_und_s_m: cls_discount_factor):

        if self.tenor.maturity_date > spot_rate.tenor.maturity_date or self.tenor.maturity_date < spot_rate.tenor.maturity_date :

            if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_base_s_m.ask / df_und_s_m.bid - 1),
                    spot_rate.mid *
                    (df_base_s_m.bid / df_und_s_m.ask - 1))

            elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_und_s_m.ask / df_base_s_m.bid - 1),
                    spot_rate.mid *
                    (df_und_s_m.bid / df_base_s_m.ask - 1))

        elif self.tenor.maturity_date == spot_rate.tenor.maturity_date:
            self.set_rate_by_bid_ask(0, 0)

        else:
            pass


class cls_fx_rate_curve:
    def __init__(self, currency: cls_currency, fx_rate_list: list):

        if fx_rate_list is not None:
            fx_rate_list.sort(
                key=lambda fx_rate: fx_rate.tenor.start_date, reverse=False)
            fx_rate_list.sort(
                key=lambda fx_rate: fx_rate.tenor.maturity_date, reverse=False)
            self.fx_rate_list = fx_rate_list
        else:
            self.fx_rate_list = []

        self.currency = currency





class cls_discount_factor_curve(cls_fx_rate_curve):
    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 linearization: linearization_enum):
        super().__init__(currency, fx_rate_list)
        self.linearization = linearization

    @property
    def today_date(self)->datetime.date:
        return self.fx_rate_list[0]

    def get_discount_factor_by_interpolation(
            self,
            df_early: cls_discount_factor,
            df_late: cls_discount_factor,
            tenor_mid: cls_tenor,
            linearization: linearization_enum) -> cls_discount_factor:

        if linearization == linearization_enum.log_ds_factor:
            value_of_df_mid = 10 ** ((math.log10(df_late.mid) - math.log10(df_early.mid)) / (df_late.tenor.number_of_days - df_early.tenor.number_of_days) * (tenor_mid.number_of_days - df_early.tenor.number_of_days) + math.log10(df_early.mid))
            return cls_discount_factor(df_early.currency, tenor_mid, value_of_df_mid)
        elif linearization == linearization_enum.linear_ds_rate:

            ds_rate_late = df_late.get_discount_rate()
            ds_rate_early = df_early.get_discount_rate()

            value_of_ds_mid = (ds_rate_late.mid - ds_rate_early.mid) / (
                ds_rate_late.tenor.number_of_days -
                ds_rate_early.tenor.number_of_days
            ) * (tenor_mid.number_of_days - ds_rate_early.tenor.number_of_days
                 ) + ds_rate_early.mid

            return cls_discount_rate(df_early.currency, tenor_mid, value_of_ds_mid).get_discount_factor()
        else:
            return None

    def get_discount_factor_by_maturity_date(
            self, maturity_date: datetime.date) -> cls_discount_factor:

        #search in existing tenor
        for discount_factor_iter in self.fx_rate_list:
            if discount_factor_iter.tenor.maturity_date == maturity_date:
                return discount_factor_iter

        #interpolation
        tenor_mid = cls_tenor(self.fx_rate_list[-1].tenor.start_date, maturity_date)

        # print("tenor_mid.start_date is ", tenor_mid.start_date, "tenor_mid.maturity_date is ", tenor_mid.maturity_date)

        if maturity_date == tenor_mid.start_date:
            # print("maturity_date == tenor_mid.start_date")
            return cls_discount_factor(self.fx_rate_list[0].currency, cls_tenor(tenor_mid.start_date, maturity_date), 1)
        elif maturity_date > tenor_mid.maturity_date:
            # print("The target maturity date is ", maturity_date, ". The max maturity date in curve is ", tenor_mid.maturity_date)
            return None
        else:
            previous_df = self.fx_rate_list[0]
            for discount_factor_iter in self.fx_rate_list:

                if discount_factor_iter.tenor.maturity_date > maturity_date:
                    df_late = discount_factor_iter
                    # print("df_late's maturity date is " +
                    #      df_late.tenor.maturity_date.strftime('%Y-%m-%d'))

                    df_early = previous_df
                    # print("df_early's maturity date is " +
                    #      df_early.tenor.maturity_date.strftime('%Y-%m-%d'))

                    return self.get_discount_factor_by_interpolation(
                        df_early, df_late, tenor_mid, self.linearization)

                previous_df = discount_factor_iter

    def get_discount_factor_by_start_maturity(self, start_date: datetime.date, maturity_date: datetime.date) -> cls_discount_factor:

        # print("get_discount_factor_by_tenor ", "tenor_input.start_date is ", tenor_input.start_date, "tenor_input.maturity_date is ", tenor_input.maturity_date)

        df_today_maturity = self.get_discount_factor_by_maturity_date(maturity_date)
        # print("get_discount_factor_by_tenor ", "df_today_maturity.tenor.start_date is ", df_today_maturity.tenor.start_date, "df_today_maturity.tenor.maturity_date is ", df_today_maturity.tenor.maturity_date)

        df_today_start = self.get_discount_factor_by_maturity_date(start_date)
        # print("get_discount_factor_by_tenor ", "df_today_start.tenor.start_date is ", df_today_start.tenor.start_date, "df_today_start.tenor.maturity_date is ", df_today_start.tenor.maturity_date)

        df_start_maturity = df_today_maturity.get_remaining_df(df_today_start, df_today_maturity.tenor.label)
        # print("get_discount_factor_by_tenor ", "df_start_maturity.tenor.start_date is ", df_start_maturity.tenor.start_date, "df_start_maturity.tenor.maturity_date is ", df_start_maturity.tenor.maturity_date)

        return df_start_maturity

    def get_discount_factor_by_label(
            self, label: str) -> cls_discount_factor:
        for discount_factor_iter in self.fx_rate_list:
            if discount_factor_iter.tenor.label == label.upper():
                return discount_factor_iter
        return None

class cls_capitalized_factor_curve(cls_fx_rate_curve):
    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 linearization: linearization_enum):

        super().__init__(currency, fx_rate_list)
        self.linearization = linearization
        self.discount_factor_curve = cls_discount_factor_curve(
            currency, [
                capitalized_factor_iter.get_discount_factor()
                for capitalized_factor_iter in self.fx_rate_list
                ], linearization)

    def get_capitalized_factor_by_maturity_date(
            self, maturity_date: datetime.date) -> cls_capitalized_factor:
        return self.discount_factor_curve.get_discount_factor_by_maturity_date(
            maturity_date).get_capitalized_factor()


class cls_market_quote_curve(cls_fx_rate_curve):

    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list):

        super().__init__(currency, fx_rate_list)



    def get_market_quote_by_label(
            self, label: str) -> cls_market_quote:
        for market_quote_iter in self.fx_rate_list:
            if market_quote_iter.tenor.label == label.upper():
                return market_quote_iter
        return None

    def get_discount_factor_on(self)->cls_discount_factor:
        market_quote_on = self.get_market_quote_by_label("O/N")

        return cls_discount_factor(
            self.currency, market_quote_on.tenor,
            1 / (1 + market_quote_on.mid *  market_quote_on.tenor.number_of_days / market_quote_on.currency.number_of_days_1year))

    def get_discount_factor_tn(self, ds_factor_on:cls_discount_factor)->cls_discount_factor:

        market_quote_tn = self.get_market_quote_by_label("T/N")
        if market_quote_tn is not None :
            ds_factor_tomorrow_next = cls_discount_factor(
            self.currency, market_quote_tn.tenor,
            1 / (1 + market_quote_tn.mid * market_quote_tn.tenor.number_of_days / market_quote_tn.currency.number_of_days_1year))
        else:
            ds_factor_tomorrow_next = cls_discount_factor(
            self.currency, cls_tenor(ds_factor_on.tenor.maturity_date,ds_factor_on.tenor.maturity_date),1 )

        return ds_factor_on.extend_by_df(ds_factor_tomorrow_next,"T/N")


    def get_discount_factor(self, tenor_label:str)->cls_discount_factor:
        if tenor_label == 'O/N':
            return self.get_discount_factor_on()

        elif tenor_label == 'T/N':
            return self.get_discount_factor_tn(self.get_discount_factor_on())

        else:
            mq = self.get_market_quote_by_label(tenor_label)
            return mq.get_discount_factor(self.get_discount_factor_tn(self.get_discount_factor_on()))


    def get_discount_factor_curve(self, linearization:linearization_enum) -> cls_discount_factor_curve:

        ds_factor_over_night = self.get_discount_factor_on()
        ds_factor_today_spot = self.get_discount_factor_tn(ds_factor_over_night)

        df_list = []

        for market_quote_iter in self.fx_rate_list:
            if market_quote_iter.tenor.label == 'O/N':
                df_iter = ds_factor_over_night
            elif market_quote_iter.tenor.label == 'T/N':
                df_iter = ds_factor_today_spot
            else:
                df_iter = market_quote_iter.get_discount_factor(ds_factor_today_spot)

            df_list.append(df_iter)
            #print("--", df_iter.tenor.label, df_iter.mid )

        return cls_discount_factor_curve(self.currency, df_list, linearization)


class cls_swap_point_panel(cls_fx_rate_curve):

    def __init__(
            self,
            currency_pair: cls_currency_pair,
            spot_rate_input: cls_fx_spot_rate,
            df_curve_base_ccy: cls_discount_factor_curve,
            df_curve_und_ccy: cls_discount_factor_curve,
            to_set_swap_point_list: bool =True):

        self.currency_pair = currency_pair
        super().__init__(currency_pair.base, [])

        self.df_curve_base_ccy = df_curve_base_ccy
        self.df_curve_und_ccy = df_curve_und_ccy

        self.spot_rate = spot_rate_input.get_fx_rate_by_quotation(currency_pair.quotation)

        if to_set_swap_point_list == True :
            logger.info("swap point list is auto set.")
            self.set_swap_point_list()
        else:
            logger.info("swap point list is not auto set.")

    @property
    def swap_point_factor(self)->int:
        return self.currency_pair.swap_point_factor

    @property
    def spot_date(self)->datetime.date:
        return self.spot_rate.tenor.maturity_date

    @property
    def today_date(self)->datetime.date:
        return self.spot_rate.tenor.start_date

    @property
    def swap_point_list(self)->list:
        return self.fx_rate_list

    def get_swap_point_from_list_by_tenor_label(self, label:str) -> cls_swap_point:

        for swap_point_iter in self.swap_point_list:
            if swap_point_iter.tenor.label == label.upper().strip():
                return swap_point_iter

        logger.warning("parameter label {label} is not found in swap point list.".format(label=label))
        return None

    def set_swap_point_list(self):
        for df_und_iter in self.df_curve_und_ccy.fx_rate_list:

            df_base_iter = self.df_curve_base_ccy.get_discount_factor_by_maturity_date(df_und_iter.tenor.maturity_date)

            if df_base_iter is not None:
                swap_point_iter = self.get_swap_point_by_start_maturity(df_und_iter.tenor.maturity_date, df_und_iter.tenor.label)
                self.swap_point_list.append(swap_point_iter)

        return self.swap_point_list

    def get_swap_point_by_start_maturity(self, maturity_date: datetime.date, label:str=None) -> cls_swap_point:

        if label == "O/N":

            df_base_spot_tom = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)
            df_und_spot_tom = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

            df_base_spot_today = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, self.today_date)
            df_und_spot_today = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, self.today_date)

            swap_point_spot_tom = self.get_swap_point_by_df(df_base_spot_tom, df_und_spot_tom)
            swap_point_spot_today = self.get_swap_point_by_df(df_base_spot_today, df_und_spot_today)

            # print("start_date=", start_date)
            # print("maturity_date=", maturity_date)
            # print("spot_date=", self.spot_date)
            # print("swap_point_spot_tom.mid=", swap_point_spot_tom.mid)
            # print("swap_point_spot_today.mid=", swap_point_spot_today.mid)

            #logger.info("swap point of tenor O/N is added to list.")

            return cls_swap_point(self.currency_pair, cls_tenor(self.today_date, maturity_date, label), swap_point_spot_tom.mid - swap_point_spot_today.mid)

        elif label == "T/N":

            date_tom = self.get_swap_point_from_list_by_tenor_label("O/N").tenor.maturity_date

            df_base_spot_tom = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, date_tom)
            df_und_spot_tom = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, date_tom)

            swap_point_spot_tom = self.get_swap_point_by_df(df_base_spot_tom, df_und_spot_tom)

            return cls_swap_point(self.currency_pair, cls_tenor(date_tom, maturity_date, label), -1 * swap_point_spot_tom.mid)

        else:
            df_base_spot_maturity = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)
            # print("get_swap_point_by_start_maturity ", "df_base_s_m.tenor.start_date is ", df_base_s_m.tenor.start_date, "df_base_s_m.tenor.maturity_date is ", df_base_s_m.tenor.maturity_date)

            df_und_spot_maturity = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

            return self.get_swap_point_by_df(df_base_spot_maturity, df_und_spot_maturity)

    def get_swap_point_by_df(
            self,
            df_base: cls_discount_factor,
            df_und: cls_discount_factor) -> cls_swap_point:

        swap_point = cls_swap_point(self.currency_pair, df_und.tenor)

        swap_point.set_swap_point_by_discount_factor(
            self.spot_rate,
            df_base,
            df_und)

        return swap_point
