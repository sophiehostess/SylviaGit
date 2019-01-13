
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

def get_reversed_quotation_mode(quotation_mode:quotation_mode_enum)->quotation_mode_enum:
    if quotation_mode == quotation_mode_enum.base_und:
        return quotation_mode_enum.und_base
    elif quotation_mode == quotation_mode_enum.und_base:
        return quotation_mode_enum.base_und


def get_reversed_quotation(quotation:str)->str:
    return quotation[0:3] + quotation[3:4] + quotation[4:7]


class linearization_enum(Enum):
    # Interpolate Log(DiscountFactor) linearly
    log_ds_factor = "log_ds_factor"

    # Interpolate DiscountRate linearly
    linear_ds_rate = "linear_ds_rate"

    #interpolate DiscountRate*Time linearly
    linear_rate_time = "linear_rate_time"

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

class date_shift_enum(Enum):
    D0 = 0
    D1 = 1
    D2 = 2


class cls_currency:
    def __init__(self,
                 label: str=None,
                 number_of_days_1year: int=365,
                 spot_date_shift: date_shift_enum = date_shift_enum.D2):
        self.label = label.upper() if label is not None else label
        self.number_of_days_1year = number_of_days_1year
        self.spot_date_shift = spot_date_shift


class cls_currency_pair:
    def __init__(self,
                 base: cls_currency,
                 underlying: cls_currency,
                 quotation_mode: quotation_mode_enum,
                 swap_point_factor: int=10000,
                 day_shift: date_shift_enum = None):
        self.base = base
        self.underlying = underlying

        self.quotation_mode = quotation_mode
        self.swap_point_factor = swap_point_factor

        if day_shift is None:
            self.day_shift = base.spot_date_shift if base.spot_date_shift._value_ >= underlying.spot_date_shift._value_ else underlying.spot_date_shift
        else:
            self.day_shift = day_shift

        self.__quotation = ""

        if quotation_mode == quotation_mode_enum.base_und:
            self.__quotation = build_quotation(base.label, underlying.label)
        elif quotation_mode == quotation_mode_enum.und_base:
            self.__quotation = build_quotation(underlying.label, base.label)
        else:
            assert("quotation_mode is invalid")
            logger.critical("{class_name} : parameter quotation_mode {quotation_mode} is invalid".format(class_name=self.__class__.__name__.replace("cls_",""),  quotation_mode=quotation_mode.__repr__()))
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

    @property
    def label(self)->str:
        if self.quotation_mode == quotation_mode_enum.base_und:
            return self.base.label + "/" + self.underlying.label
        elif self.quotation_mode == quotation_mode_enum.und_base:
            return self.underlying.label + "/" + self.base.label



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
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
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
    def mid(self, mid:float):
        self.set_rate_by_mid_spread(mid, self.__spread)

    @property
    def bid(self)->float:
        return self.__bid

    @bid.setter
    def bid(self, bid:float):
        self.set_rate_by_bid_ask(bid, self.__ask)

    @property
    def ask(self)->float:
        return self.__ask

    @ask.setter
    def ask(self, ask:float):
        self.set_rate_by_bid_ask(self.__bid, ask)

    @property
    def spread(self)->float:
        return self.__spread

    @spread.setter
    def spread(self, spread:float):
        self.set_rate_by_mid_spread(self.__mid, spread)

    @property
    def value(self)->float:
        return self.__mid

    @value.setter
    def value(self, value:float):
        self.set_rate_by_mid_spread(value, self.__spread)

class cls_single_currency_rate(cls_rate):
    def __init__(self,
                 currency: cls_currency=None,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0,
                 basis: int=None):
        self.currency = currency
        self.tenor = tenor

        if basis is not None:
            self.basis = basis
        else:
            self.basis = currency.number_of_days_1year


        super().__init__(mid, bid, ask)
        self.__unique_key = self.__get_unique_key()

    def __get_unique_key(self)->str:
        return (self.__class__.__name__.replace("cls_","") + "#" +
                self.currency.label + "#" +
                self.tenor.start_date.strftime('%Y-%m-%d') + "#" +
                self.tenor.maturity_date.strftime('%Y-%m-%d'))

    @property
    def unique_key(self):
        return self.__unique_key

    @property
    def currency_label(self):
        return self.currency.label

    @property
    def start_date(self):
        return self.tenor.start_date

    @property
    def maturity_date(self):
        return self.tenor.maturity_date

    @property
    def label(self):
        return self.tenor.label


class cls_discount_factor(cls_single_currency_rate):
    def get_capitalized_factor(self):
        return cls_capitalized_factor(self.currency, self.tenor, 1 / self.mid, basis=self.basis)

    def get_discount_rate(self)->cls_single_currency_rate:

        # to review
        return cls_discount_rate(
            self.currency, self.tenor, (1 / self.mid - 1) *
                                       self.basis / self.tenor.number_of_days, basis=self.basis)

    def get_remaining_df(self, df1, label: str=None):

        # assume self = df1 * df2
        # get df2

        if self.tenor.start_date == df1.tenor.start_date:

            df2_tenor = cls_tenor(df1.tenor.maturity_date,
                                  self.tenor.maturity_date,
                                  label if label is not None else None)

            return cls_discount_factor(df1.currency, df2_tenor, self.mid / df1.mid, basis=self.basis)

        elif self.tenor.maturity_date == df1.tenor.maturity_date:

            df2_tenor = cls_tenor(self.tenor.start_date,
                                  df1.tenor.start_date,
                                  label if label is not None else None)

            return cls_discount_factor(df1.currency, df2_tenor, self.mid / df1.mid, basis=self.basis)

        elif self.tenor.start_date == df1.tenor.start_date and self.tenor.maturity_date == df1.tenor.maturity_date and self.mid != df1.mid:
            logger.critical("parameter df1 tenor start data: %s maturity date: %s match current start date: %s maturity date: %s, but df value %s does not match %s", df1.start_date, df1.maturity_date, self.start_date, self.maturity_date, df1.value, self.value)
            return None


        else:
            logger.critical("parameter df1 tenor start data: %s maturity date: %s does not match current start date: %s maturity date: %s", df1.start_date, df1.maturity_date, self.start_date, self.maturity_date)
            return None

    def extend_by_df(self, df1, label: str=None):
        # assume df2 = self * df1
        # get df2

        if self.tenor.maturity_date == df1.tenor.start_date:

            df2_tenor = cls_tenor(self.tenor.start_date,
                                  df1.tenor.maturity_date, label if label is not None else None)

            return cls_discount_factor(self.currency, df2_tenor, self.mid * df1.mid, basis=self.basis)

        elif df1.tenor.maturity_date == self.tenor.start_date:

            df2_tenor = cls_tenor(df1.tenor.start_date,
                                  self.tenor.maturity_date, label if label is not None else None)

            return cls_discount_factor(self.currency, df2_tenor, df1.mid * self.mid, basis=self.basis)

        else:
            logger.critical("parameter df1 tenor start data: %s maturity date: %s does not match current start date: %s maturity date: %s", df1.tenor.start_date, df1.tenor.maturity_date, self.tenor.start_date, self.tenor.maturity_date)
            return None


class cls_capitalized_factor(cls_single_currency_rate):
    def get_discount_factor(self) -> cls_discount_factor:
        return cls_discount_factor(self.currency, self.tenor, 1 / self.mid, basis=self.basis)

    def get_discount_rate(self)->cls_single_currency_rate:
        return cls_discount_rate(
            self.currency, self.tenor, (self.mid - 1) * self.basis / self.tenor.number_of_days, basis=self.basis)


class cls_market_quote(cls_single_currency_rate):
    def get_discount_rate(self, discount_factor_today_spot: cls_discount_factor)->cls_single_currency_rate:

        # to be reviewed
        if self.maturity_date > discount_factor_today_spot.maturity_date:
            number_of_days_spot_to_maturity = self.tenor.number_of_days
            number_of_days_today_to_maturity = discount_factor_today_spot.tenor.number_of_days + number_of_days_spot_to_maturity

            ds_rate_value = self.basis * (
                1 / discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_spot_to_maturity / self.basis) - 1
            ) / number_of_days_today_to_maturity

            return cls_discount_rate(self.currency,
                                     cls_tenor(discount_factor_today_spot.start_date, self.maturity_date, self.tenor.label ),
                                     ds_rate_value,
                                     basis=self.basis)


        # for O/N of T+1 currency
        if self.currency.spot_date_shift == date_shift_enum.D1 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            return cls_discount_rate(self.currency,
                                     cls_tenor(self.start_date, self.maturity_date, self.tenor.label ),
                                     self.value,
                                     basis=self.basis)

        # for T/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date > discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            # to enhance
            pass

        # for O/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date < discount_factor_today_spot.maturity_date:
            return cls_discount_rate(self.currency,
                                     cls_tenor(self.start_date, self.maturity_date, self.tenor.label ),
                                     self.value,
                                     basis=self.basis)


    # only applicable to maturity date <= 1Y
    def get_discount_factor_today_maturity(self, discount_factor_today_spot: cls_discount_factor)->cls_discount_factor:

        if self.maturity_date > discount_factor_today_spot.maturity_date:
            number_of_days_spot_to_maturity = self.tenor.number_of_days

            ds_factor_value = discount_factor_today_spot.mid * ( 1 / (  1 + self.mid * number_of_days_spot_to_maturity / self.basis) )

            return cls_discount_factor(self.currency,
                                       cls_tenor(discount_factor_today_spot.start_date, self.maturity_date, self.tenor.label),
                                       ds_factor_value,
                                       basis=self.basis)

        # for O/N of T+1 currency
        if self.currency.spot_date_shift == date_shift_enum.D1 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            return discount_factor_today_spot

        # for T/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date > discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            number_of_days_tom_to_next = self.tenor.number_of_days

            ds_factor_value = discount_factor_today_spot.mid / (1 / (1 + self.mid * number_of_days_tom_to_next / self.basis) )

            return cls_discount_factor(self.currency,
                                     cls_tenor(discount_factor_today_spot.start_date, self.maturity_date, self.tenor.label),
                                     ds_factor_value,
                                     basis=self.basis)

        # for O/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date < discount_factor_today_spot.maturity_date:
            return cls_discount_factor(self.currency,
                                      cls_tenor(self.start_date, self.maturity_date, self.tenor.label),
                                      self.mid,
                                      basis=self.basis)


    # only applicable to maturity date <= 1Y
    def get_discount_factor_spot_maturity(self, ds_factor_value_input:float=None)->cls_discount_factor:

        number_of_days_spot_to_maturity = self.tenor.number_of_days

        if ds_factor_value_input is None:
            ds_factor_value = 1 / (  1 + self.mid * number_of_days_spot_to_maturity / self.basis)
        else:
            ds_factor_value = ds_factor_value_input

        return cls_discount_factor(self.currency,
                                   cls_tenor(self.start_date, self.maturity_date, self.tenor.label),
                                   ds_factor_value,
                                   basis=self.basis)


class cls_discount_rate(cls_single_currency_rate):
    def get_discount_factor(self)->cls_discount_factor:
        return cls_discount_factor(self.currency,
                                   self.tenor,
                                   1 / (1 + self.mid * self.tenor.number_of_days / self.basis),
                                   basis=self.basis)

    def get_capitalized_factor(self)->cls_capitalized_factor:
        return cls_capitalized_factor(self.currency,
                                      self.tenor,
                                      1 + self.mid * self.basis / self.tenor.number_of_days,
                                      basis=self.basis)

    def get_market_quote(self, discount_factor_today_spot: cls_discount_factor
                         ) -> cls_market_quote:

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_today_to_maturity = self.tenor.number_of_days
            number_of_days_spot_to_maturity = number_of_days_today_to_maturity - discount_factor_today_spot.tenor.number_of_days


            # to review
            market_quote_value = self.basis * (
                discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_today_to_maturity / self.basis) - 1
            ) / number_of_days_spot_to_maturity

            return cls_market_quote(self.currency,
                                    cls_tenor(discount_factor_today_spot.tenor.maturity_date,
                                    self.tenor.maturity_date), market_quote_value,
                                    basis=self.basis)

        # for O/N of T+1 currency
        if self.currency.spot_date_shift == date_shift_enum.D1 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            return cls_market_quote(self.currency,
                                    cls_tenor(self.start_date, self.maturity_date, self.tenor.label),
                                    self.mid,
                                    basis=self.basis)

        # for T/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date > discount_factor_today_spot.start_date and self.maturity_date == discount_factor_today_spot.maturity_date:
            # to enhance
            pass

        # for O/N of T+2 currency
        if  self.currency.spot_date_shift == date_shift_enum.D2 and self.start_date == discount_factor_today_spot.start_date and self.maturity_date < discount_factor_today_spot.maturity_date:
            return cls_market_quote(self.currency,
                                    cls_tenor(self.start_date, self.maturity_date, self.tenor.label),
                                    self.mid,
                                    basis=self.basis)


class cls_overnight_funding_rate(cls_single_currency_rate):
    pass

class cls_on_funding_rate_panel:
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



class cls_deal_price(cls_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 maturity_date: datetime.date,
                 value: float=0,
                 quotation_mode: quotation_mode_enum = None):
        self.currency_pair = currency_pair
        self.maturity_date = maturity_date
        super().__init__(value, value, value)

        if quotation_mode is None:
            self.quotation_mode = self.currency_pair.quotation_mode
        else:
            self.quotation_mode = quotation_mode

    @property
    def value(self):
        return self.mid

    @value.setter
    def value(self, value:float):
        self.set_rate_by_mid_spread(value)


    def get_deal_price_by_quotation_mode(self,quotation_mode: quotation_mode_enum):
        if quotation_mode == self.quotation_mode:
            return self
        else:
            return self.get_reversed_deal_price()

    def get_reversed_deal_price(self)->cls_rate:
        return cls_deal_price(self.currency_pair, self.maturity_date, 1/self.value, get_reversed_quotation_mode(self.quotation_mode))


class cls_currency_pair_rate(cls_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0,
                 quotation_mode: quotation_mode_enum=None):
        self.currency_pair = currency_pair
        self.tenor = tenor
        super().__init__(mid, bid, ask)
        self.__unique_key = self.__get_unique_key()

        if quotation_mode is None:
            self.quotation_mode = self.currency_pair.quotation_mode
        else:
            self.quotation_mode = quotation_mode

    def __get_unique_key(self)->str:
        return (self.__class__.__name__.replace("cls_","") + "#" +
                self.currency_pair.quotation + "#" +
                self.tenor.start_date.strftime('%Y-%m-%d') + "#" +
                self.tenor.maturity_date.strftime('%Y-%m-%d'))

    @property
    def unique_key(self):
        return self.__unique_key

    @property
    def maturity_date(self)->datetime.date:
        return self.tenor.maturity_date

    @property
    def start_date(self)->datetime.date:
        return self.tenor.start_date

    @property
    def label(self)->str:
        return self.tenor.label

    @property
    def quotation(self)->str:
        if self.quotation_mode == quotation_mode_enum.base_und:
            return build_quotation(self.currency_pair.base.label, self.currency_pair.underlying.label)
        elif self.quotation_mode == quotation_mode_enum.und_base:
            return build_quotation(self.currency_pair.underlying.label, self.currency_pair.base.label)


class cls_fx_rate(cls_currency_pair_rate):
    def get_reversed_fx_rate(self):
        return cls_fx_rate(self.currency_pair, self.tenor,
                           1 / self.mid, 1 / self.bid, 1 / self.ask, get_reversed_quotation_mode(self.quotation_mode))

    def get_fx_rate_by_quotation_mode(self,
                                      quotation_mode: quotation_mode_enum):
        if quotation_mode == self.quotation_mode:
            return self
        else:
            return self.get_reversed_fx_rate()

    def get_fx_rate_by_quotation(self, quotation: str):
        if quotation == self.quotation:
            return self
        elif quotation == get_reversed_quotation(self.quotation):
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
                 ask: float=0,
                 quotation_mode: quotation_mode_enum = None):

        super().__init__(currency_pair, tenor, mid, bid, ask, quotation_mode)
        self.tenor.label = "SPT"
        # print(str(self.mid))

    def get_spot_cls(self, fx_rate: cls_fx_rate):
        return cls_fx_spot_rate(fx_rate.currency_pair, fx_rate.tenor,
                                fx_rate.mid, fx_rate.bid, fx_rate.ask, fx_rate.quotation_mode)

    def get_fx_rate_by_quotation(self, quotation: str):
        if quotation == self.quotation:
            return self
        elif quotation == get_reversed_quotation(self.quotation):
            return self.get_spot_cls(self.get_reversed_fx_rate())
        else:
            logger.critical("parameter quotation {quotation}is invalid.".format(quotation=quotation))
            return None


    def get_fx_rate_by_quotation_mode(self, quotation_mode: quotation_mode_enum):
        if quotation_mode == self.quotation_mode:
            return self
        else:
            return self.get_reversed_fx_rate()

    def get_reversed_fx_rate(self):
        return self.get_spot_cls(cls_fx_rate(self.currency_pair, self.tenor, 1 / self.mid, 1 / self.bid, 1 / self.ask, get_reversed_quotation_mode(self.quotation_mode)))



    def get_discounted_spot_rate(self, base_ccy_df_t_s:cls_discount_factor, und_ccy_df_t_s:cls_discount_factor)->cls_fx_rate:

        tenor = cls_tenor(self.start_date, self.start_date)

        if self.quotation_mode == quotation_mode_enum.base_und :
            return self.get_spot_cls(cls_fx_rate(self.currency_pair, tenor, self.mid * und_ccy_df_t_s.value / base_ccy_df_t_s.value, quotation_mode=self.quotation_mode))
        else:
            return self.get_spot_cls(cls_fx_rate(self.currency_pair, tenor, self.mid * base_ccy_df_t_s.value / und_ccy_df_t_s.value, quotation_mode=self.quotation_mode))

    @property
    def spot_date(self)->datetime.date:
        return self.tenor.maturity_date


class cls_fx_forward_rate(cls_fx_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0,
                 quotation_mode: quotation_mode_enum = None):
        super().__init__(currency_pair, tenor, mid, bid, ask, quotation_mode)

        self.__spot_rate = cls_fx_spot_rate(currency_pair, tenor, mid, bid, ask, quotation_mode)
        self.__swap_point = cls_swap_point(currency_pair, tenor, 0, 0, 0) #multiped by factor

    @property
    def swap_point_factor(self)->float:
        return self.currency_pair.swap_point_factor

    @property
    def spot_rate(self)->cls_fx_spot_rate:
        return self.__spot_rate


    @spot_rate.setter
    def spot_rate(self, spot_rate: cls_fx_rate):
        self.__spot_rate.set_rate_by_mid_bid_ask(
            spot_rate.mid, spot_rate.bid, spot_rate.ask)
        self.set_rate_by_mid_bid_ask(
            spot_rate.mid +
            self.__swap_point.mid / self.swap_point_factor,
            spot_rate.bid +
            self.__swap_point.bid / self.swap_point_factor,
            spot_rate.ask +
            self.__swap_point.ask / self.swap_point_factor)

    @property
    def swap_point_value_with_factor(self)->float:
        #mutiplied with swap point factor
        return self.__swap_point.mid

    @property
    def swap_point_value_in_unit(self)->float:
        return self.__swap_point.mid / self.swap_point_factor

    @property
    def swap_point(self)->cls_currency_pair_rate:
        return self.__swap_point


    @swap_point.setter
    def swap_point(self, swap_point_with_factor: cls_currency_pair_rate):
        self.set_rate_by_mid_bid_ask(
            swap_point_with_factor.mid, swap_point_with_factor.bid, swap_point_with_factor.ask)

        self.set_rate_by_mid_bid_ask(
            self.__spot_rate.mid + swap_point_with_factor.mid / self.swap_point_factor,
            self.__spot_rate.bid + swap_point_with_factor.bid / self.swap_point_factor,
            self.__spot_rate.ask + swap_point_with_factor.ask / self.swap_point_factor)

    def set_forward_rate_by_spot_and_df(
            self,
            spot_rate: cls_fx_spot_rate,
            base_ccy_df_s_m: cls_discount_factor, #base currency discount factor spot date to maturity date
            und_ccy_df_s_m: cls_discount_factor): #underlying currency discount factor spot date to maturity date

        spot_rate_with_aligned_quotation_mode = spot_rate.get_fx_rate_by_quotation_mode(self.currency_pair.quotation_mode)

        # quotation is base-und
        if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
            self.mid = spot_rate_with_aligned_quotation_mode.mid * (base_ccy_df_s_m.mid / und_ccy_df_s_m.mid )

        # quotation is und-base
        elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
            self.mid = spot_rate_with_aligned_quotation_mode.mid * (und_ccy_df_s_m.mid / base_ccy_df_s_m.mid )


    def set_forward_rate_by_discounted_spot_and_df(
            self,
            discounted_spot_rate: cls_fx_rate,
            base_ccy_df_t_m: cls_discount_factor, #base currency discount factor spot date to maturity date
            und_ccy_df_t_m: cls_discount_factor): #underlying currency discount factor spot date to maturity date

        discounted_spot_rate_with_aligned_quotation_mode = discounted_spot_rate.get_fx_rate_by_quotation_mode(self.currency_pair.quotation_mode)

        # quotation is base-und
        if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
            self.mid =  discounted_spot_rate_with_aligned_quotation_mode.mid * (base_ccy_df_t_m.mid / und_ccy_df_t_m.mid)

        # quotation is und-base
        elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
            self.mid = discounted_spot_rate_with_aligned_quotation_mode.mid * (und_ccy_df_t_m.mid / base_ccy_df_t_m.mid)

    def set_forward_rate_by_spot_and_swp(self,
                                         spot_rate: cls_fx_spot_rate,
                                         swap_point: cls_currency_pair_rate):
        self.spot_rate = spot_rate
        self.swap_point = swap_point


def create_forward_rate_by_spot_and_df(currency_pair: cls_currency_pair,
                                       tenor: cls_tenor,
                                       spot_rate: cls_fx_spot_rate,
                                       base_ccy_df_s_m: cls_discount_factor,
                                       und_ccy_df_s_m: cls_discount_factor)->cls_fx_forward_rate:

    spot_rate_with_aligned_quotation_mode = spot_rate.get_fx_rate_by_quotation_mode(currency_pair.quotation_mode)

    # quotation is base-und
    if currency_pair.quotation_mode == quotation_mode_enum.base_und:
        forward_rate_value = spot_rate_with_aligned_quotation_mode.mid * (base_ccy_df_s_m.mid / und_ccy_df_s_m.mid)

    # quotation is und-base
    elif currency_pair.quotation_mode == quotation_mode_enum.und_base:
        forward_rate_value = spot_rate_with_aligned_quotation_mode.mid * (und_ccy_df_s_m.mid / base_ccy_df_s_m.mid)

    else:
        forward_rate_value = 0

    return cls_fx_forward_rate(currency_pair, tenor, forward_rate_value)


def create_forward_rate_by_discounted_spot_and_df(currency_pair: cls_currency_pair,
                                                  tenor: cls_tenor,
                                                  discounted_spot_rate: cls_fx_rate,
                                                  base_ccy_df_t_m: cls_discount_factor,
                                                  und_ccy_df_t_m: cls_discount_factor)->cls_fx_forward_rate:

    discounted_spot_rate_with_aligned_quotation_mode = discounted_spot_rate.get_fx_rate_by_quotation_mode(currency_pair.quotation_mode)

    # quotation is base-und
    if currency_pair.quotation_mode == quotation_mode_enum.base_und:
        forward_rate_value = discounted_spot_rate_with_aligned_quotation_mode.mid * (base_ccy_df_t_m.mid / und_ccy_df_t_m.mid)

    # quotation is und-base
    elif currency_pair.quotation_mode == quotation_mode_enum.und_base:
        forward_rate_value = discounted_spot_rate_with_aligned_quotation_mode.mid * (und_ccy_df_t_m.mid / base_ccy_df_t_m.mid)

    else:
        forward_rate_value = 0

    return cls_fx_forward_rate(currency_pair, tenor, forward_rate_value)




class cls_fx_discounted_spot_rate(cls_fx_forward_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)
        self.tenor.label = "TDY"


class cls_swap_point(cls_currency_pair_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        super().__init__(currency_pair, tenor, mid, bid, ask)

    def set_swap_point_by_forward_rate_and_spot(
                                                self, spot_rate: cls_fx_spot_rate,
                                                forward_rate: cls_fx_forward_rate):

        spot_rate_with_aligned_quotation_mode = spot_rate.get_fx_rate_by_quotation_mode(self.currency_pair.quotation_mode)
        forward_rate_with_aligned_quotation_mode = forward_rate.get_fx_rate_by_quotation_mode(self.currency_pair.quotation_mode)

        self.mid = (forward_rate_with_aligned_quotation_mode.mid - spot_rate_with_aligned_quotation_mode.mid) * self.currency_pair.swap_point_factor

    def set_swap_point_by_discount_factors(
            self,
            spot_rate: cls_fx_spot_rate,
            df_base_s_m: cls_discount_factor,
            df_und_s_m: cls_discount_factor):

        # for maturity is not spot date
        if self.tenor.maturity_date > spot_rate.tenor.maturity_date or self.tenor.maturity_date < spot_rate.tenor.maturity_date :

            # quotation is base-und
            if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_base_s_m.ask / df_und_s_m.bid - 1),
                    spot_rate.mid *
                    (df_base_s_m.bid / df_und_s_m.ask - 1))

            # quotation is und-base
            elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_und_s_m.ask / df_base_s_m.bid - 1),
                    spot_rate.mid *
                    (df_und_s_m.bid / df_base_s_m.ask - 1))

        # for maturity is spot date
        # always return 0
        elif self.tenor.maturity_date == spot_rate.tenor.maturity_date:
            self.set_rate_by_bid_ask(0, 0)

        else:
            pass

    @property
    def swap_point_factor(self)->int:
        return self.currency_pair.swap_point_factor

    @property
    def swap_point_value_multi_by_factor(self)->float:
        return self.mid * self.swap_point_factor


class cls_rate_curve:
    def __init__(self, fx_rate_list: list):

        # sort by maturity date, then start date
        if fx_rate_list is not None:
            fx_rate_list.sort(
                key=lambda fx_rate: fx_rate.tenor.start_date, reverse=False)
            fx_rate_list.sort(
                key=lambda fx_rate: fx_rate.tenor.maturity_date, reverse=False)
            self.fx_rate_list = fx_rate_list
        else:
            logger.info("Empty rate curve is created")
            self.fx_rate_list = []

    @property
    def max_maturiy_date(self)->datetime.date:
        return self.fx_rate_list[-1].tenor.maturity_date


class cls_single_currency_rate_curve(cls_rate_curve):
    def __init__(self, currency: cls_currency, fx_rate_list: list, basis:int=None):

        super().__init__(fx_rate_list)
        self.currency = currency

        if basis is not None:
            self.basis = basis
        else:
            self.basis = currency.number_of_days_1year

    @property
    def spot_date_shift(self)->date_shift_enum:
        return self.currency.spot_date_shift

    @property
    def currency_label(self):
        return self.currency.label


    def get_item_by_label(self, label:str):
        for iter in self.fx_rate_list:
            if iter.tenor.label == label.upper():
                return iter
        else:
            return None



class cls_discount_factor_curve(cls_single_currency_rate_curve):
    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 linearization: linearization_enum,
                 basis: int = None):
        super().__init__(currency, fx_rate_list, basis)
        self.linearization = linearization

    def get_discount_factor_by_interpolation(
            self,
            df_early: cls_discount_factor,
            df_late: cls_discount_factor,
            tenor_mid: cls_tenor,
            linearization: linearization_enum,
            basis:int)->cls_discount_factor:

        if linearization == linearization_enum.log_ds_factor:
            value_of_df_mid = 10 ** ((math.log10(df_late.mid) - math.log10(df_early.mid)) / (df_late.tenor.number_of_days - df_early.tenor.number_of_days) * (tenor_mid.number_of_days - df_early.tenor.number_of_days) + math.log10(df_early.mid))
            return cls_discount_factor(df_early.currency, tenor_mid, value_of_df_mid, basis=basis)

        elif linearization == linearization_enum.linear_ds_rate:

            ds_rate_late = df_late.get_discount_rate()
            ds_rate_early = df_early.get_discount_rate()

            value_of_ds_mid = (ds_rate_late.mid - ds_rate_early.mid) / (
                ds_rate_late.tenor.number_of_days -
                ds_rate_early.tenor.number_of_days
            ) * (tenor_mid.number_of_days - ds_rate_early.tenor.number_of_days
                 ) + ds_rate_early.mid

            return cls_discount_rate(df_early.currency, tenor_mid, value_of_ds_mid, basis=basis).get_discount_factor()

        elif linearization == linearization_enum.linear_rate_time:
            #to be enhanced
            pass

        else:
            return None

    def get_discount_factor_by_maturity_date(
            self, maturity_date: datetime.date) -> cls_discount_factor:

        #search in existing tenor
        for ds_factor_iter in self.fx_rate_list:
            if ds_factor_iter.tenor.maturity_date == maturity_date:
                return ds_factor_iter

        #interpolation
        else:
            #create the target tenor
            tenor_mid = cls_tenor(self.today_date, maturity_date)

            # print("tenor_mid.start_date is ", tenor_mid.start_date, "tenor_mid.maturity_date is ", tenor_mid.maturity_date)

            if maturity_date == tenor_mid.start_date:
                # print("maturity_date == tenor_mid.start_date")
                return cls_discount_factor(self.currency, cls_tenor(tenor_mid.start_date, maturity_date), 1, basis=self.basis)
            elif maturity_date > self.max_maturiy_date:
                # print("The target maturity date is ", maturity_date, ". The max maturity date in curve is ", tenor_mid.maturity_date)
                # need extrapolation

                return self.get_discount_factor_by_interpolation(self.fx_rate_list[-2], self.fx_rate_list[-1], tenor_mid, self.linearization, self.basis)

            else:
                # find out the discount factor earlier than target one , and the one later than target one
                previous_df = self.fx_rate_list[0]
                for ds_factor_iter in self.fx_rate_list:

                    if ds_factor_iter.tenor.maturity_date > maturity_date:
                        df_late = ds_factor_iter
                        # print("df_late's maturity date is " +
                        #      df_late.tenor.maturity_date.strftime('%Y-%m-%d'))

                        df_early = previous_df
                        # print("df_early's maturity date is " +
                        #      df_early.tenor.maturity_date.strftime('%Y-%m-%d'))

                        return self.get_discount_factor_by_interpolation(df_early, df_late, tenor_mid, self.linearization, self.basis)

                    previous_df = ds_factor_iter

    def get_discount_factor_by_start_maturity(self, start_date: datetime.date, maturity_date: datetime.date) -> cls_discount_factor:

        # print("get_discount_factor_by_tenor ", "tenor_input.start_date is ", tenor_input.start_date, "tenor_input.maturity_date is ", tenor_input.maturity_date)

        df_today_maturity = self.get_discount_factor_by_maturity_date(maturity_date)
        # print("get_discount_factor_by_tenor ", "df_today_maturity.tenor.start_date is ", df_today_maturity.tenor.start_date, "df_today_maturity.tenor.maturity_date is ", df_today_maturity.tenor.maturity_date)

        df_today_start = self.get_discount_factor_by_maturity_date(start_date)
        # print("get_discount_factor_by_tenor ", "df_today_start.tenor.start_date is ", df_today_start.tenor.start_date, "df_today_start.tenor.maturity_date is ", df_today_start.tenor.maturity_date)


        if start_date != maturity_date:
            df_start_maturity = df_today_maturity.get_remaining_df(df_today_start, df_today_maturity.tenor.label)
        else:
            df_start_maturity = cls_discount_factor(self.currency, cls_tenor(start_date, start_date), 1, basis=self.basis)
        # print("get_discount_factor_by_tenor ", "df_start_maturity.tenor.start_date is ", df_start_maturity.tenor.start_date, "df_start_maturity.tenor.maturity_date is ", df_start_maturity.tenor.maturity_date)

        return df_start_maturity

    def get_discount_factor_by_label(
            self, label: str) -> cls_discount_factor:

        return self.get_item_by_label(label)

        # for ds_factor_iter in self.fx_rate_list:
        #     if ds_factor_iter.tenor.label == label.upper():
        #         return ds_factor_iter
        # else:
        #     return None


    def get_neighbor_tenor_dates_by_maturity_date(
            self, maturity_date: datetime.date) -> tuple:

        #search in existing tenor
        for ds_factor_iter in self.fx_rate_list:
            if ds_factor_iter.tenor.maturity_date == maturity_date:
                return (maturity_date, maturity_date)

        else:

            # find out the discount factor earlier than target one , and the one later than target one
            previous_df = self.fx_rate_list[0]
            for ds_factor_iter in self.fx_rate_list:

                if ds_factor_iter.tenor.maturity_date > maturity_date:
                    df_late = ds_factor_iter

                    df_early = previous_df

                    return (df_early.maturity_date, df_late.maturity_date)

                previous_df = ds_factor_iter

    def get_neighbor_discount_factors_by_maturity_date(
            self, maturity_date: datetime.date) -> tuple:

        #search in existing tenor
        for ds_factor_iter in self.fx_rate_list:
            if ds_factor_iter.tenor.maturity_date == maturity_date:
                return (maturity_date, maturity_date)

        else:

            # find out the discount factor earlier than target one , and the one later than target one
            previous_df = self.fx_rate_list[0]
            for ds_factor_iter in self.fx_rate_list:

                if ds_factor_iter.tenor.maturity_date > maturity_date:
                    df_late = ds_factor_iter

                    df_early = previous_df

                    return (df_early, df_late)

                previous_df = ds_factor_iter


    @property
    def today_date(self)->datetime.date:
        return self.get_discount_factor_by_label('O/N').tenor.start_date

    @property
    def tom_date(self) -> datetime.date:
        return self.get_discount_factor_by_label('O/N').tenor.maturity_date

    @property
    def spot_date(self) -> datetime.date:
        if self.spot_date_shift == date_shift_enum.D1 :
            return self.get_discount_factor_by_label('O/N').tenor.maturity_date
        elif self.spot_date_shift == date_shift_enum.D2 :
            return self.get_discount_factor_by_label('T/N').tenor.maturity_date
        elif self.spot_date_shift == date_shift_enum.D0 :
            return self.get_discount_factor_by_label('O/N').tenor.start_date


class cls_capitalized_factor_curve(cls_single_currency_rate_curve):
    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 linearization: linearization_enum,
                 basis: int=None):

        super().__init__(currency, fx_rate_list, basis)
        self.linearization = linearization
        self.discount_factor_curve = cls_discount_factor_curve(currency, [capitalized_factor_iter.get_discount_factor_by_label()
                                                                          for capitalized_factor_iter in self.fx_rate_list
                                                                         ],
                                                               linearization,
                                                               basis
                                                               )

    def get_capitalized_factor_by_maturity_date(self, maturity_date: datetime.date) -> cls_capitalized_factor:
        return self.discount_factor_curve.get_discount_factor_by_maturity_date(
            maturity_date).get_capitalized_factor()


def get_1Ybackwardshifted_tenor_label(input_tenor_label:str)->str:
    shifted_tenor_label = None
    if input_tenor_label is None:
        pass
    elif input_tenor_label == "13M":
        shifted_tenor_label = "1M"
    elif input_tenor_label == "14M":
        shifted_tenor_label = "2M"
    elif input_tenor_label == "15M":
        shifted_tenor_label = "3M"
    elif input_tenor_label == "16M":
        shifted_tenor_label = "4M"
    elif input_tenor_label == "17M":
        shifted_tenor_label = "5M"
    elif input_tenor_label == "18M":
        shifted_tenor_label = "6M"
    elif input_tenor_label == "19M":
        shifted_tenor_label = "7M"
    elif input_tenor_label == "20M":
        shifted_tenor_label = "8M"
    elif input_tenor_label == "21M":
        shifted_tenor_label = "9M"
    elif input_tenor_label == "22M":
        shifted_tenor_label = "10M"
    elif input_tenor_label == "23M":
        shifted_tenor_label = "11M"
    elif input_tenor_label == "2Y":
        shifted_tenor_label = "1Y"
    elif input_tenor_label == "30M":
        shifted_tenor_label = "18M"
    elif input_tenor_label == "3Y":
        shifted_tenor_label = "2Y"
    elif input_tenor_label == "4Y":
        shifted_tenor_label = "3Y"
    elif input_tenor_label == "5Y":
        shifted_tenor_label = "4Y"
    elif input_tenor_label == "6Y":
        shifted_tenor_label = "5Y"
    elif input_tenor_label == "7Y":
        shifted_tenor_label = "6Y"
    elif input_tenor_label == "8Y":
        shifted_tenor_label = "7Y"
    elif input_tenor_label == "9Y":
        shifted_tenor_label = "8Y"
    elif input_tenor_label == "10Y":
        shifted_tenor_label = "9Y"
    else:
        shifted_tenor_label = str(int(input_tenor_label[0:-1]) - 1) + input_tenor_label[-1]

    return shifted_tenor_label


class cls_market_quote_curve(cls_single_currency_rate_curve):

    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 basis: int=None):

        super().__init__(currency, fx_rate_list, basis)

    def get_market_quote_by_label(self, label: str) -> cls_market_quote:

        return self.get_item_by_label(label)

        # for market_quote_iter in self.fx_rate_list:
        #     if market_quote_iter.tenor.label == label.upper():
        #         return market_quote_iter
        # else:
        #     return None

    def __get_discount_factor_on(self)->cls_discount_factor:
        market_quote_on = self.get_market_quote_by_label("O/N")

        return cls_discount_factor(
            self.currency, market_quote_on.tenor,
            1 / (1 + market_quote_on.mid * market_quote_on.tenor.number_of_days / market_quote_on.basis), basis=self.basis)

    def __get_discount_factor_tn(self, ds_factor_on:cls_discount_factor)->cls_discount_factor:

        market_quote_tn = self.get_market_quote_by_label("T/N")
        if market_quote_tn is not None :
            ds_factor_tomorrow_next = cls_discount_factor(
            self.currency, market_quote_tn.tenor,
            1 / (1 + market_quote_tn.mid * market_quote_tn.tenor.number_of_days / market_quote_tn.basis), basis=self.basis)
        else:
            ds_factor_tomorrow_next = cls_discount_factor(
            self.currency, cls_tenor(ds_factor_on.tenor.maturity_date,ds_factor_on.tenor.maturity_date),1 , basis=self.basis)

        return ds_factor_on.extend_by_df(ds_factor_tomorrow_next,"T/N")

    # to be tested
    def get_discount_factor_today_spot(self)->cls_discount_factor:

        ds_factor_on = self.__get_discount_factor_on()

        if self.spot_date_shift == date_shift_enum.D1:
            return ds_factor_on

        elif self.spot_date_shift == date_shift_enum.D2:
            return self.__get_discount_factor_tn(ds_factor_on)

        elif self.spot_date_shift == date_shift_enum.D0:
            return cls_discount_factor(self.currency, cls_tenor(self.today_date, self.today_date, "TDY"), 1, basis=self.basis)


    def get_discount_factor_by_label(self, tenor_label:str)->cls_discount_factor:
        if tenor_label == 'O/N':
            return self.__get_discount_factor_on()

        elif tenor_label == 'T/N':
            return self.get_discount_factor_today_spot()

        else:
            market_quote = self.get_market_quote_by_label(tenor_label)
            if market_quote is None:
                assert("tenor label {tenor_label} is not found in market quote curve".format(tenor_label=tenor_label))
                return None
            else:
                return market_quote.get_discount_factor_today_maturity(self.get_discount_factor_today_spot())


    def get_market_quote_backwardshifted(self, input_tenor_label:str)->cls_market_quote:

        mq_input_tenor = self.get_market_quote_by_label(input_tenor_label)
        mq_1Y = self.get_market_quote_by_label('1Y')

        # already within 1Y
        if mq_input_tenor.maturity_date <= mq_1Y.maturity_date:
            return mq_input_tenor

        # greater than 1Y
        else:
            shifted_tenor_label = get_1Ybackwardshifted_tenor_label(input_tenor_label)
            mq_backward_1Y_shifted = self.get_market_quote_by_label(shifted_tenor_label)

            while mq_backward_1Y_shifted is None and shifted_tenor_label is not None :
                shifted_tenor_label = get_1Ybackwardshifted_tenor_label(shifted_tenor_label)
                mq_backward_1Y_shifted = self.get_market_quote_by_label(shifted_tenor_label)
            else:
                assert ("backwardshifted tenor not found")

            if mq_backward_1Y_shifted.maturity_date <= mq_1Y.maturity_date:
                return mq_backward_1Y_shifted
            else:
                return self.get_market_quote_backwardshifted(shifted_tenor_label)


    def get_market_quote_list_backwardshifted(self, input_tenor_label:str, market_quote_list_input:list=None)->list:

        mq_input_tenor = self.get_market_quote_by_label(input_tenor_label)
        mq_1Y = self.get_market_quote_by_label('1Y')

        # recursive called
        if market_quote_list_input is not None :
            mq_result_list = market_quote_list_input

        # initial called
        else:
            mq_result_list = []

        # already within 1Y
        if mq_input_tenor.maturity_date <= mq_1Y.maturity_date:
            return [mq_input_tenor]

        # greater than 1Y
        else:
            shifted_tenor_label = get_1Ybackwardshifted_tenor_label(input_tenor_label)
            mq_backward_1Y_shifted = self.get_market_quote_by_label(shifted_tenor_label)

            # work around only
            while mq_backward_1Y_shifted is None and shifted_tenor_label is not None :
                shifted_tenor_label = get_1Ybackwardshifted_tenor_label(shifted_tenor_label)
                mq_backward_1Y_shifted = self.get_market_quote_by_label(shifted_tenor_label)

            if mq_backward_1Y_shifted is not None:
                mq_result_list.append(mq_backward_1Y_shifted)
            else:
                assert("not able to find the backward shifted tenor for {input_tenor_label}".format(input_tenor_label=input_tenor_label))
                # to be enhanced

            # if the result is within 1Y, then return the list
            if mq_backward_1Y_shifted.maturity_date <= mq_1Y.maturity_date:

                # sort and make the list ascending
                mq_result_list.reverse()
                return mq_result_list

            # oherwise continue to get the tenor(s) until it is within 1Y
            else:
                return self.get_market_quote_list_backwardshifted(shifted_tenor_label, mq_result_list)



    def get_discount_factor_curve(self, linearization:linearization_enum, basis_input:int=None) -> cls_discount_factor_curve:

        if basis_input is None:
            basis = self.basis
        else:
            basis = basis_input

        discount_factor_today_spot = self.get_discount_factor_today_spot()

        ds_factor_list = []

        market_quote_1Y = self.get_discount_factor_by_label('1Y')

        for market_quote_iter in self.fx_rate_list:
            if market_quote_iter.tenor.label == 'O/N':
                discount_factor_iter = self.__get_discount_factor_on()
            elif market_quote_iter.tenor.label == 'T/N':
                discount_factor_iter = discount_factor_today_spot
            else:

                if market_quote_1Y is None :
                    discount_factor_iter = market_quote_iter.get_discount_factor_today_maturity(discount_factor_today_spot)

                elif market_quote_iter.maturity_date <= market_quote_1Y.maturity_date :
                    discount_factor_iter = market_quote_iter.get_discount_factor_today_maturity(discount_factor_today_spot)

                else:

                    #market_quote_backwardshifted_within_1Y = self.get_market_quote_backwardshifted(market_quote_iter.label)
                    market_quote_list_backwardshifted = self.get_market_quote_list_backwardshifted(market_quote_iter.label)

                    discount_factor_iter = get_discounted_factor_today_maturity_from_market_quote_over_1Ys(discount_factor_today_spot, market_quote_list_backwardshifted, market_quote_iter)

            ds_factor_list.append(discount_factor_iter)

            #print("--", df_iter.tenor.label, df_iter.mid )

        return cls_discount_factor_curve(self.currency, ds_factor_list, linearization, basis)

    @property
    def spot_date(self)->datetime.date:
        if self.spot_date_shift == date_shift_enum.D1:
            return self.get_market_quote_by_label('O/N').tenor.maturity_date

        elif self.spot_date_shift == date_shift_enum.D2:
            return self.get_market_quote_by_label('T/N').tenor.maturity_date

        elif self.spot_date_shift == date_shift_enum.D0:
            return self.get_market_quote_by_label('O/N').tenor.start_date

        else:
            assert("invalid spot date shift")

    @property
    def today_date(self)->datetime.date:
        return self.get_market_quote_by_label('O/N').tenor.start_date

    @property
    def last_item(self)->cls_market_quote:
        return self.fx_rate_list[-1]


def get_discounted_factor_spot_maturity_from_market_quote_over_1Y(discount_factor_spot_backwardshifteddate:cls_discount_factor, market_quote_spot_maturity:cls_market_quote)->cls_discount_factor:
    #                                                       |<-----------------1 year--------->|
    # |-------------------|---------------------------------|-------------------------|--------|-------------------time axis--->
    # today-----------spot date------------intermediate interest payment date -------1Y------maturity date


    # for easy calculation only , any positive amount is workable. Not refecting in  result.
    virtual_principal = 1000000

    cash_flow_principal_spot_date = virtual_principal
    cash_flow_principal_maturity = -1 * virtual_principal

    # duration is spot to intermediate interest payment date
    cash_flow_intermediate_interest = -1 * virtual_principal * (market_quote_spot_maturity.value * discount_factor_spot_backwardshifteddate.tenor.number_of_days / discount_factor_spot_backwardshifteddate.basis)

    discounted_cash_flow_intermediate_interest = cash_flow_intermediate_interest * discount_factor_spot_backwardshifteddate.value

    # including principal and maturity payment
    discounted_cash_flow_maturity = 0 - cash_flow_principal_spot_date - discounted_cash_flow_intermediate_interest

    # duration is intermediate interest payment date to maturity date
    # equal to (spot date to maturity date minus spot date to intermediate interest payment date)
    cash_flow_maturity_interest = -1 * virtual_principal * (market_quote_spot_maturity.value * (market_quote_spot_maturity.tenor.number_of_days - discount_factor_spot_backwardshifteddate.tenor.number_of_days) / discount_factor_spot_backwardshifteddate.basis)

    discount_factor_spot_maturity_value = discounted_cash_flow_maturity / (cash_flow_maturity_interest + cash_flow_principal_maturity)

    discount_factor_spot_maturity = market_quote_spot_maturity.get_discount_factor_spot_maturity(discount_factor_spot_maturity_value)

    return discount_factor_spot_maturity




def get_discounted_factor_today_maturity_from_market_quote_over_1Y(discount_factor_today_spot:cls_discount_factor,
                                                                   market_quote_spot_backwardshifteddate:cls_market_quote,
                                                                   market_quote_spot_maturity:cls_market_quote
                                                                  )->cls_discount_factor:
    # backward shift date is the interpayment date
    discount_factor_spot_interpayment = market_quote_spot_backwardshifteddate.get_discount_factor_spot_maturity()

    discount_factor_spot_maturity = get_discounted_factor_spot_maturity_from_market_quote_over_1Y(discount_factor_spot_interpayment, market_quote_spot_maturity)

    discount_factor_today_maturity = discount_factor_today_spot.extend_by_df(discount_factor_spot_maturity, discount_factor_spot_maturity.label)

    return discount_factor_today_maturity



def get_discounted_factor_spot_maturity_from_market_quote_over_1Ys(discount_factor_list_spot_backwardshifteddate:list, market_quote_spot_maturity:cls_market_quote)->cls_discount_factor:
    #                                                            |<-----------------1 year------------>|<--------------------1 year--------->|
    # |-------------------|--------------------------------------|-------------------|-----------------|----------------------------|--------|-------------------time axis--->
    # today-----------spot date----------intermediate interest payment date1--------1Y---intermediate interest payment date2-------2Y------maturity date


    # for easy calculation only , any positive amount is workable. Not refecting in result.
    virtual_principal = 1000000

    cash_flow_spot_date_principal = virtual_principal
    cash_flow_maturity_principal = -1 * virtual_principal

    # sum up the intermediate discounted interest payment
    discounted_cash_flow_intermediate_interest_sum = 0

    aggregated_days = 0

    for discount_factor_spot_backwardshifteddate in discount_factor_list_spot_backwardshifteddate :
        # duration is last intermediate payment date  to current intermediate payment date
        cash_flow_intermediate_interest = -1 * virtual_principal * (market_quote_spot_maturity.value * (discount_factor_spot_backwardshifteddate.tenor.number_of_days - aggregated_days )/ discount_factor_spot_backwardshifteddate.basis)

        # get the discounted amount of the cash flow , discounted from intermediate payment date to spot date.
        discounted_cash_flow_intermediate_interest = cash_flow_intermediate_interest * discount_factor_spot_backwardshifteddate.value


        discounted_cash_flow_intermediate_interest_sum = discounted_cash_flow_intermediate_interest_sum + discounted_cash_flow_intermediate_interest
        aggregated_days = discount_factor_spot_backwardshifteddate.tenor.number_of_days

    # including principal and maturity payment
    discounted_cash_flow_maturity = 0 - cash_flow_spot_date_principal - discounted_cash_flow_intermediate_interest_sum

    # duration is the last intermediate interest payment date to maturity date
    # equal to ( spot date to maturity date   MINUS   spot date to last intermediate interest payment date  )
    discount_factor_spot_lastinterpayment = discount_factor_list_spot_backwardshifteddate[-1]

    cash_flow_maturity_interest = -1 * virtual_principal * (market_quote_spot_maturity.value * (market_quote_spot_maturity.tenor.number_of_days - discount_factor_spot_lastinterpayment.tenor.number_of_days) / discount_factor_spot_lastinterpayment.basis)

    discount_factor_spot_maturity_value = discounted_cash_flow_maturity / (cash_flow_maturity_interest + cash_flow_maturity_principal)

    discount_factor_spot_maturity = market_quote_spot_maturity.get_discount_factor_spot_maturity(discount_factor_spot_maturity_value)

    return discount_factor_spot_maturity


def get_discounted_factor_today_maturity_from_market_quote_over_1Ys(discount_factor_today_spot:cls_discount_factor,
                                                                    market_quote_list_spot_backwardshifteddate:list,
                                                                    market_quote_spot_maturity:cls_market_quote
                                                                   )->cls_discount_factor:
    discount_factor_list =[]

    market_quote_list = market_quote_list_spot_backwardshifteddate + [market_quote_spot_maturity]

    #market_quote_spot_backwardshifteddate_iter = cls_market_quote()

    for i in range(len(market_quote_list) - 1):
        if i == 0:
            # assume the first one is within 1Y
            market_quote_spot_backwardshifteddate_iter = market_quote_list[i]

            # for the market quote within 1Y, discount factor could be calculated directly.
            discount_factor_spot_backwardshifteddate_iter = market_quote_spot_backwardshifteddate_iter.get_discount_factor_spot_maturity()
            discount_factor_list.append(discount_factor_spot_backwardshifteddate_iter)

        else:
            pass

        # the next payment date as iterated maturity date
        market_quote_spot_next_backwardshifteddate_iter = market_quote_list[i + 1]

        discount_factor_spot_maturity_iter = get_discounted_factor_spot_maturity_from_market_quote_over_1Ys(discount_factor_list, market_quote_spot_next_backwardshifteddate_iter)

        # add result to discount factor list
        discount_factor_list.append(discount_factor_spot_maturity_iter)

    else:
        discount_factor_spot_maturity = discount_factor_list[-1]
        discount_factor_today_maturity = discount_factor_today_spot.extend_by_df(discount_factor_spot_maturity, discount_factor_spot_maturity.label)

    return discount_factor_today_maturity



class cls_swap_point_panel(cls_rate_curve):

    def __init__(
            self,
            currency_pair: cls_currency_pair,
            spot_rate_input: cls_fx_spot_rate=None,
            df_curve_base_ccy: cls_discount_factor_curve=None,
            df_curve_und_ccy: cls_discount_factor_curve=None,
            set_swap_point_list_when_initial: bool = True):

        self.currency_pair = currency_pair
        super().__init__([])

        self.df_curve_base_ccy = df_curve_base_ccy
        self.df_curve_und_ccy = df_curve_und_ccy

        self.spot_rate = spot_rate_input.get_fx_rate_by_quotation(currency_pair.quotation)

        if set_swap_point_list_when_initial == True :
            #logger.info("swap point list is auto set.")
            self.refresh_swap_point_list()
        else:
            pass
            #logger.info("swap point list is not auto set.")

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

    @property
    def base_currency_label(self)->str:
        return self.currency_pair.base.label

    @property
    def und_currency_label(self)->str:
        return self.currency_pair.underlying.label

    def get_swap_point_from_list_by_tenor_label(self, label:str) -> cls_swap_point:

        for swap_point_iter in self.swap_point_list:
            if swap_point_iter.tenor.label == label.upper().strip():
                return swap_point_iter
        else:
            logger.warning("parameter label {label} is not found in swap point list.".format(label=label))
            return None


    def get_swap_point_from_list_by_maturity(self, maturity_date: datetime.date) -> cls_swap_point:

        for swap_point_iter in self.swap_point_list:
            if swap_point_iter.tenor.maturity_date == maturity_date:
                return swap_point_iter
        else:
            logger.warning("parameter maturity_date {maturity_date} is not found in swap point list.".format(maturity_date=maturity_date.__str__()))
            return None



    def refresh_swap_point_list(self):
        # follow the tenors of underlying currency
        for df_und_iter in self.df_curve_und_ccy.fx_rate_list:

            df_base_iter = self.df_curve_base_ccy.get_discount_factor_by_maturity_date(df_und_iter.tenor.maturity_date)

            if df_base_iter is not None:
                swap_point_iter = self.get_swap_point_by_maturity(df_und_iter.tenor.maturity_date)
                self.swap_point_list.append(swap_point_iter)

        return self.swap_point_list

    def get_swap_point_by_maturity(self, maturity_date: datetime.date) -> cls_swap_point:

        if maturity_date == self.df_curve_und_ccy.tom_date :

            df_base_spot_tom = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)
            df_und_spot_tom = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

            df_base_spot_today = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, self.today_date)
            df_und_spot_today = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, self.today_date)

            swap_point_spot_tom = self.__set_and_return_swap_point_by_df(df_base_spot_tom, df_und_spot_tom)
            swap_point_spot_today = self.__set_and_return_swap_point_by_df(df_base_spot_today, df_und_spot_today)

            return cls_swap_point(self.currency_pair, cls_tenor(self.today_date, maturity_date, 'O/N'), swap_point_spot_tom.mid - swap_point_spot_today.mid)

        elif maturity_date == self.df_curve_und_ccy.spot_date and self.df_curve_und_ccy.spot_date_shift == date_shift_enum.D2:

            date_tom = self.get_swap_point_from_list_by_tenor_label("O/N").tenor.maturity_date

            df_base_spot_tom = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, date_tom)
            df_und_spot_tom = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, date_tom)

            swap_point_spot_tom = self.__set_and_return_swap_point_by_df(df_base_spot_tom, df_und_spot_tom)

            return cls_swap_point(self.currency_pair, cls_tenor(date_tom, maturity_date, 'T/N'), -1 * swap_point_spot_tom.mid)

        elif maturity_date == self.df_curve_und_ccy.spot_date and self.df_curve_und_ccy.spot_date_shift == date_shift_enum.D0:

            return cls_swap_point(self.currency_pair, cls_tenor(maturity_date, maturity_date, 'TDY'),  0)

        else:
            df_base_spot_maturity = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)
            # print("get_swap_point_by_start_maturity ", "df_base_s_m.tenor.start_date is ", df_base_s_m.tenor.start_date, "df_base_s_m.tenor.maturity_date is ", df_base_s_m.tenor.maturity_date)

            df_und_spot_maturity = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

            return self.__set_and_return_swap_point_by_df(df_base_spot_maturity, df_und_spot_maturity)

    def __set_and_return_swap_point_by_df(
                            self,
                            df_base: cls_discount_factor,
                            df_und: cls_discount_factor) -> cls_swap_point:

        swap_point = cls_swap_point(self.currency_pair, df_und.tenor)

        swap_point.set_swap_point_by_discount_factors(
                                                    self.spot_rate,
                                                    df_base,
                                                    df_und)

        return swap_point

    def get_forwrd_rate_by_maturity(self, maturity_date:datetime.date)->cls_fx_forward_rate:

        df_base_spot_maturity = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

        df_und_spot_maturity = self.df_curve_und_ccy.get_discount_factor_by_start_maturity(self.spot_date, maturity_date)

        if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
            forward_rate_value = self.spot_rate.mid * df_base_spot_maturity.mid / df_und_spot_maturity.mid
        elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
            forward_rate_value = self.spot_rate.mid * df_und_spot_maturity.mid / df_base_spot_maturity.mid

        return cls_fx_forward_rate(self.currency_pair, cls_tenor(self.today_date, maturity_date),
                                   forward_rate_value, quotation_mode=self.currency_pair.quotation_mode)


    # get underlying currency discount factor curve by base currency discount factor curve and swap point
    def get_und_df_curve_by_swap_point_list(self, linearization_of_df_curve_und:linearization_enum, basis_input: int=None)->cls_discount_factor_curve:

        und_ccy = self.currency_pair.underlying

        if basis_input is None :
            basis = und_ccy.number_of_days_1year
        else:
            basis = basis_input


        df_list_und = []

        swap_point_on = self.get_swap_point_from_list_by_tenor_label("O/N")


        # get swap point of today --> spot date
        if und_ccy.spot_date_shift == date_shift_enum.D2:
            swap_point_tn = self.get_swap_point_from_list_by_tenor_label("T/N")

            swap_point_today_spot_value = swap_point_on.value + swap_point_tn.value
            swap_point_today_spot = cls_swap_point(self.currency_pair, cls_tenor(self.today_date, self.spot_date), swap_point_today_spot_value)

        elif und_ccy.spot_date_shift == date_shift_enum.D1:
            swap_point_today_spot = cls_swap_point(self.currency_pair, cls_tenor(self.today_date, self.spot_date), swap_point_on.value)

        elif und_ccy.spot_date_shift == date_shift_enum.D0:
            swap_point_today_spot = cls_swap_point(self.currency_pair, cls_tenor(self.today_date, self.today_date), 0)

        else:
            pass

        # get discount factor of underlying currency , today --> spot
        df_base_today_spot = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.today_date, self.spot_date)
        if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
            df_und_today_spot_value = df_base_today_spot.value * (1 - swap_point_today_spot.value / self.spot_rate.value )


        elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
            df_und_today_spot_value = df_base_today_spot.value / (1 - swap_point_today_spot.value / self.spot_rate.value )

        else:
            pass

        if und_ccy.spot_date_shift == date_shift_enum.D2:
            df_und_today_spot = cls_discount_factor(und_ccy, cls_tenor(self.today_date, self.spot_date, "T/N"), df_und_today_spot_value, basis=basis)
        elif und_ccy.spot_date_shift == date_shift_enum.D1:
            df_und_today_spot = cls_discount_factor(und_ccy, cls_tenor(self.today_date, self.spot_date, "O/N"), df_und_today_spot_value, basis=basis)
        elif und_ccy.spot_date_shift == date_shift_enum.D0:
            df_und_today_spot = cls_discount_factor(und_ccy, cls_tenor(self.today_date, self.spot_date, "TDY"), 1, basis=basis)
        else:
            pass

        #print("df_und_today_spot_value={df_und_today_spot_value}".format(df_und_today_spot_value=df_und_today_spot_value))
        df_list_und.append(df_und_today_spot) # append discount factor "T/N" to result



        # get discount factor of underlying currency , today -> tom , and others
        for swap_point_iter in self.fx_rate_list:

            df_base_spot_maturity = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(self.spot_date, swap_point_iter.maturity_date)

            if swap_point_iter.label == "O/N":
                pass

            elif swap_point_iter.label == "T/N" and und_ccy.spot_date_shift == date_shift_enum.D2:
                df_base_tom_spot = self.df_curve_base_ccy.get_discount_factor_by_start_maturity(swap_point_iter.start_date, self.spot_date)

                if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
                    df_und_tom_spot_value = df_base_tom_spot.value * (1 - swap_point_iter.value / self.spot_rate.value)

                elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
                    df_und_tom_spot_value = df_base_tom_spot.value / (1 - swap_point_iter.value / self.spot_rate.value)

                else:
                    pass

                df_und_today_tom_value = df_und_today_spot.value / df_und_tom_spot_value

                df_und_today_tom = cls_discount_factor(und_ccy, cls_tenor(self.today_date, swap_point_iter.maturity_date, "O/N"), df_und_today_tom_value, basis=basis)

                #print("df_und_on_value={df_und_on_value}".format(df_und_on_value=df_und_today_tom_value))
                df_list_und.append(df_und_today_tom) # append discount factor "O/N" to result

            else:
                if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
                    df_und_spot_maturity_value = df_base_spot_maturity.value / (swap_point_iter.value / self.spot_rate.value + 1)

                elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
                    df_und_spot_maturity_value = df_base_spot_maturity.value * (swap_point_iter.value / self.spot_rate.value + 1)

                else:
                    pass

                df_und_today_maturity_value = df_und_today_spot_value * df_und_spot_maturity_value

                df_und_today_maturity = cls_discount_factor(und_ccy,
                                                            cls_tenor(self.today_date, swap_point_iter.maturity_date, swap_point_iter.label),
                                                            df_und_today_maturity_value,
                                                            basis=basis)

                df_list_und.append(df_und_today_maturity) # append discount factor greater than "T/N" to result

        df_curve_und = cls_discount_factor_curve(und_ccy, df_list_und, linearization_of_df_curve_und, basis=basis)
        return df_curve_und

    def get_and_set_und_df_curve_by_swap_point_list(self, linearization_of_df_curve_und:linearization_enum):
        self.df_curve_und_ccy = self.get_und_df_curve_by_swap_point_list(linearization_of_df_curve_und)


def create_swap_point_panel_by_market_quote_curves(currency_pair: cls_currency_pair,
                                                   spot_rate_input: cls_fx_spot_rate,
                                                   mq_curve_base_ccy: cls_market_quote_curve,
                                                   mq_curve_und_ccy: cls_market_quote_curve,
                                                   df_curve_base_linearization: linearization_enum = linearization_enum.log_ds_factor,
                                                   df_curve_und_linearization: linearization_enum = linearization_enum.log_ds_factor,
                                                   df_curve_base_basis: int=None,
                                                   df_curve_und_basis: int=None,
                                                   set_swap_point_list_when_initial: bool = False
                                                   )->cls_swap_point_panel:

    df_curve_base_ccy = mq_curve_base_ccy.get_discount_factor_curve(df_curve_base_linearization,df_curve_base_basis)
    df_curve_und_ccy = mq_curve_und_ccy.get_discount_factor_curve(df_curve_und_linearization, df_curve_und_basis)

    return cls_swap_point_panel(currency_pair, spot_rate_input, df_curve_base_ccy, df_curve_und_ccy, set_swap_point_list_when_initial)


class cls_rate_dict:
    def __init__(self ,
                 today_date: datetime.date,
                 curve_dict: dict=None):
        self.today_date = today_date
        self.curve_dict = {} if curve_dict is None else curve_dict

    def get_curve_by_currency_label(self, currency_label:str)->cls_discount_factor_curve:
        if currency_label in self.curve_dict:
            return self.curve_dict[currency_label]
        else:
            return None

    def add_curve_to_dict(self, label:str, curve:cls_rate_curve)->None:
        self.curve_dict[label] = curve

    def remove_curve_from_dict(self, label:str)->None:
        del self.curve_dict[label]

    def clear_dict(self)->None:
        self.curve_dict.clear()


class cls_discount_factor_curve_dict(cls_rate_dict):
    def get_swap_point_panel_by_currency_pair(self,currency_pair:cls_currency_pair, spot_rate:cls_fx_spot_rate)->cls_swap_point_panel:

        if currency_pair.base.label in self.curve_dict:
            df_curve_base_ccy = self.get_curve_by_currency_label(currency_pair.base.label)
        else:
            assert("currency {label} is not in dict".format(label=currency_pair.base.label))
            return None

        if currency_pair.underlying.label in self.curve_dict:
            df_curve_und_ccy = self.get_curve_by_currency_label(currency_pair.underlying.label)
        else:
            assert ("currency {label} is not in dict".format(label=currency_pair.underlying.label))
            return None

        return cls_swap_point_panel(currency_pair, spot_rate, df_curve_base_ccy, df_curve_und_ccy)


class cls_market_quote_curve_dict(cls_rate_dict):

    def get_discount_factor_curve_dict(self, linearization:linearization_enum)->cls_discount_factor_curve_dict:
        df_curve_dict = cls_discount_factor_curve_dict(self.today_date)

        for ccy_label, mq_curve_iter in self.curve_dict.items():
            df_curve_iter = mq_curve_iter.get_discount_factor_curve(linearization, mq_curve_iter.basis)
            if ccy_label in df_curve_dict.curve_dict:
                assert("ccy_name {ccy_name} is already in df_curve_dict".format(ccy_name=ccy_label))
            else:
                pass
            df_curve_dict.curve_dict[ccy_label] = df_curve_iter

        return df_curve_dict