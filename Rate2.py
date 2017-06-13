#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import math
#import bisect

#def xenum(**enums):
#    return type('Enum', (), enums)

#Numbers = xenum(ONE=1, TWO=2, THREE='three')

from enum import Enum


def build_quotation(ccy1: str, ccy2: str):
    return ccy1 + '-' + ccy2


class quotation_mode_enum(Enum):
    base_und = "base-und"
    und_base = "und-base"


class linearization_enum(Enum):
    log_ds_factor = "log_ds_factor"
    linear_ds_rate = "linear_ds_rate"


class cls_currency:
    def __init__(self,
                 label: str,
                 factor: int=1,
                 number_of_days_1year: int=365):
        self.label = label.upper()
        self.factor = factor
        self.number_of_days_1year = number_of_days_1year


class cls_currency_pair:
    def __init__(self,
                 base: cls_currency,
                 underlying: cls_currency,
                 quotation_mode: quotation_mode_enum,
                 swap_point_factor: int=10000,
                 number_of_days_1year: int=360,
                 day_shift: int=2):
        self.base = base
        self.underlying = underlying

        self.quotation_mode = quotation_mode
        self.swap_point_factor = swap_point_factor

        self.number_of_days_1year = number_of_days_1year

        self.day_shift = day_shift
        self.__quotation = ""

        if quotation_mode == quotation_mode_enum.base_und:
            self.__quotation = build_quotation(base.label, underlying.label)
        elif quotation_mode == quotation_mode_enum.und_base:
            self.__quotation = build_quotation(underlying.label, base.label)

        #print("quotation is " + self.__quotation)

    @property
    def quotation(self):
        return self.__quotation

    def get_reversed_quotation_mode(self) -> quotation_mode_enum:
        if self.quotation_mode == quotation_mode_enum.base_und:
            quotation_mode = quotation_mode_enum.und_base
        elif self.quotation_mode == quotation_mode_enum.und_base:
            quotation_mode = quotation_mode_enum.base_und
        else:
            quotation_mode = quotation_mode_enum.und_base

        #print("quotation_mode is " + self.quotation_mode.__repr__())
        return quotation_mode

    def get_reversed_pair(self):
        return cls_currency_pair(self.base, self.underlying,
                                 self.get_reversed_quotation_mode(),
                                 self.swap_point_factor,
                                 self.number_of_days_1year, self.day_shift)


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
    def number_of_days(self):
        return self.__number_of_days

    def get_inverse_tenor(self, label: str=None):
        return cls_tenor(self.maturity_date, self.start_date,
                         (self.label + " inverse") if label is None else label)

        #print(self.start_date.strftime('%Y-%m-%d'))
        #print(self.maturity_date.strftime('%Y-%m-%d'))
        #print(self.number_of_days)

        #print(self.label + " " + str(self.start_date) + " " + str(self.maturity_date))


class cls_rate:
    def __init__(self,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.tenor = tenor
        self.__mid = 0
        self.__bid = 0
        self.__ask = 0
        self.__spread = 0

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

        if not spread is None:
            self.__spread = spread

        self.__bid = self.__mid - self.__spread
        self.__ask = self.__mid + self.__spread

    @property
    def mid(self):
        return self.__mid

    @mid.setter
    def mid(self, mid):
        self.set_rate_by_mid_spread(mid, self.__spread)

    @property
    def bid(self):
        return self.__bid

    @bid.setter
    def bid(self, bid):
        self.set_rate_by_bid_ask(bid, self.__ask)

    @property
    def ask(self):
        return self.__ask

    @ask.setter
    def ask(self, ask):
        self.set_rate_by_bid_ask(self.__bid, ask)

    @property
    def spread(self):
        return self.__spread

    @spread.setter
    def spread(self, spread):
        self.set_rate_by_mid_spread(self.__mid, spread)


class cls_single_currency_rate(cls_rate):
    def __init__(self,
                 currency: cls_currency=None,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.currency = currency
        super().__init__(tenor, mid, bid, ask)


class cls_discount_factor(cls_single_currency_rate):
    def get_capitalized_factor(self):
        return cls_capitalized_factor(self.currency, self.tenor, 1 / self.mid)

    def get_discount_rate(self):
        return cls_discount_rate(
            self.currency, self.tenor, (1 / self.mid - 1) *
            self.currency.number_of_days_1year / self.tenor.number_of_days)

    def get_remaining_df(self, df1):

        # assume self = df1 * df2

        if self.tenor.start_date == df1.tenor.start_date and self.tenor.maturity_date > df1.tenor.maturity_date:

            df2_tenor = cls_tenor(df1.tenor.maturity_date,
                                  self.tenor.maturity_date)

            return cls_discount_factor(df1.currency, df2_tenor,
                                       self.mid / df1.mid)


class cls_capitalized_factor(cls_single_currency_rate):
    def get_discount_factor(self) -> cls_discount_factor:
        return cls_discount_factor(self.currency, self.tenor, 1 / self.mid)

    def get_discount_rate(self):
        return cls_discount_rate(
            self.currency, self.tenor, (self.mid - 1) * self.currency.number_of_days_1year / self.tenor.number_of_days)


class cls_market_quote(cls_single_currency_rate):
    def get_discount_factor(self,
                            discount_factor_today_spot: cls_discount_factor):

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_spot_to_maturity = self.tenor.number_of_days
            number_of_days_today_to_maturity = discount_factor_today_spot.tenor.number_of_days + number_of_days_spot_to_maturity

            ds_value = self.currency.number_of_days_1year * self.currency.factor * (
                1 / discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_spot_to_maturity / self.
                 currency.factor / self.currency.number_of_days_1year) - 1
            ) / number_of_days_today_to_maturity

            return cls_discount_rate(
                self.currency,
                cls_tenor(discount_factor_today_spot.tenor.start_date,
                          self.tenor.maturity_date), ds_value)


class cls_discount_rate(cls_single_currency_rate):
    def get_discount_factor(self):
        return cls_discount_factor(
            self.currency, self.tenor,
            1 / (1 + self.mid * self.currency.number_of_days_1year / self.
                 tenor.number_of_days))

    def get_capitalized_factor(self):
        return cls_capitalized_factor(
            self.currency, self.tenor, 1 + self.mid *
            self.currency.number_of_days_1year / self.tenor.number_of_days)

    def get_market_quote(self, discount_factor_today_spot: cls_discount_factor
                         ) -> cls_market_quote:

        if self.tenor.maturity_date > discount_factor_today_spot.tenor.maturity_date:
            number_of_days_today_to_maturity = self.tenor.number_of_days
            number_of_days_spot_to_maturity = number_of_days_today_to_maturity - discount_factor_today_spot.tenor.number_of_days

            market_quote_value = self.currency.number_of_days_1year * self.currency.factor * (
                discount_factor_today_spot.mid *
                (1 + self.mid * number_of_days_today_to_maturity / self.
                 currency.factor / self.currency.number_of_days_1year) - 1
            ) / number_of_days_spot_to_maturity

            return cls_market_quote(
                self.currency,
                cls_tenor(discount_factor_today_spot.tenor.maturity_date,
                          self.tenor.maturity_date), market_quote_value)


class cls_currency_pair_rate(cls_rate):
    def __init__(self,
                 currency_pair: cls_currency_pair,
                 tenor: cls_tenor=None,
                 mid: float=0,
                 bid: float=0,
                 ask: float=0):
        self.currency_pair = currency_pair
        super().__init__(tenor, mid, bid, ask)


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
        #print(str(self.mid))

    def get_spot_cls(self, fx_rate: cls_fx_rate):
        return cls_fx_spot_rate(fx_rate.currency_pair, fx_rate.tenor,
                                fx_rate.mid, fx_rate.bid, fx_rate.ask)

    def get_fx_rate_by_quotation(self, quotation: str):
        if quotation == self.currency_pair.quotation:
            return self
        elif quotation == self.currency_pair.get_reversed_pair().quotation:
            return self.get_spot_cls(self.get_reversed_fx_rate())
        else:
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
    def spot_rate(self):
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
            self.__spot_rate.mid +
            swap_point_value.mid / self.currency_pair.swap_point_factor,
            self.__spot_rate.bid +
            swap_point_value.bid / self.currency_pair.swap_point_factor,
            self.__spot_rate.ask +
            swap_point_value.ask / self.currency_pair.swap_point_factor)

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
                                         spot_rate_value: cls_rate,
                                         swap_point_value: cls_rate):
        self.spot_rate = spot_rate_value
        self.swap_point = swap_point_value


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
            df_underlying_s_m: cls_discount_factor):

        if self.tenor.maturity_date > spot_rate.tenor.maturity_date:

            if self.currency_pair.quotation_mode == quotation_mode_enum.base_und:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_base_s_m.ask / df_underlying_s_m.bid - 1),
                    spot_rate.mid *
                    (df_base_s_m.bid / df_underlying_s_m.ask - 1))

            elif self.currency_pair.quotation_mode == quotation_mode_enum.und_base:
                self.set_rate_by_bid_ask(
                    spot_rate.mid *
                    (df_underlying_s_m.ask / df_base_s_m.bid - 1),
                    spot_rate.mid *
                    (df_underlying_s_m.bid / df_base_s_m.ask - 1))

        elif self.tenor.maturity_date == spot_rate.tenor.maturity_date:
            self.set_rate_by_bid_ask(0, 0)

        else:
            pass

    def set_ON_swap_point_by_discount_factor(self):
        pass

    def set_TN_swap_point_by_discount_factor(self):
        pass


#def interpolate_cf(cf_early:cls_capitalized_factor,cf_late:cls_capitalized_factor,tenor_mid:cls_tenor,linearization:linearization_enum) -> cls_capitalized_factor:
#    return(interpolate_df(cf_early.get_discount_factor(),cf_late.get_discount_factor(),tenor_mid,linearization).get_capitalized_factor())


class cls_fx_rate_curve:
    def __init__(self, currency: cls_currency, fx_rate_list: list):
        fx_rate_list.sort(
            key=lambda fx_rate: fx_rate.tenor.start_date, reverse=False)
        fx_rate_list.sort(
            key=lambda fx_rate: fx_rate.tenor.maturity_date, reverse=False)

        self.currency = currency
        self.fx_rate_list = fx_rate_list
        #debug
        for a in self.fx_rate_list:
            print(a.tenor.label)


class cls_discount_factor_curve(cls_fx_rate_curve):
    def __init__(self,
                 currency: cls_currency,
                 fx_rate_list: list,
                 linearization: linearization_enum):
        super().__init__(currency, fx_rate_list)
        self.linearization = linearization

    def get_discount_factor_by_interpolation(
            self,
            df_early: cls_discount_factor,
            df_late: cls_discount_factor,
            tenor_mid: cls_tenor,
            linearization: linearization_enum) -> cls_discount_factor:

        if linearization == linearization_enum.log_ds_factor:
            result = 10 ** (
                (math.log10(df_late.mid) - math.log10(df_early.mid)) /
                (df_late.tenor.number_of_days - df_early.tenor.number_of_days) *
                (tenor_mid.number_of_days - df_early.tenor.number_of_days) +
                math.log10(df_early.mid))
            return cls_discount_factor(df_early.currency, tenor_mid, result)
        elif linearization == linearization_enum.linear_ds_rate:

            ds_rate_late = df_late.get_discount_rate()
            ds_rate_early = df_early.get_discount_rate()

            result = (ds_rate_late.mid - ds_rate_early.mid) / (
                ds_rate_late.tenor.number_of_days -
                ds_rate_early.tenor.number_of_days
            ) * (tenor_mid.number_of_days - ds_rate_early.tenor.number_of_days
                 ) + ds_rate_early.mid

            return cls_discount_rate(df_early.currency, tenor_mid,
                                     result).get_discount_factor()
        else:
            return None

    def get_discount_factor_by_maturity_date(
            self, maturity_date: datetime.date) -> cls_discount_factor:
        #search in existing tenor
        for iter_discount_factor in self.fx_rate_list:
            if iter_discount_factor.tenor.maturity_date == maturity_date:
                return iter_discount_factor

        #interpolation
        tenor_mid = cls_tenor(self.fx_rate_list[-1].tenor.start_date,
                              maturity_date)
        print(tenor_mid.start_date)
        print(tenor_mid.maturity_date)

        previous_df = self.fx_rate_list[0]
        for iter_discount_factor in self.fx_rate_list:

            if iter_discount_factor.tenor.maturity_date > maturity_date:
                df_late = iter_discount_factor
                print("df_late's maturity date is " +
                      df_late.tenor.maturity_date.strftime('%Y-%m-%d'))

                df_early = previous_df
                print("df_early's maturity date is " +
                      df_early.tenor.maturity_date.strftime('%Y-%m-%d'))

                return self.get_discount_factor_by_interpolation(
                    df_early, df_late, tenor_mid, self.linearization)

            previous_df = iter_discount_factor

    def get_discount_factor_by_tenorlabel(
        self, tenorlabel: str) -> cls_discount_factor:
        for iter_discount_factor in self.fx_rate_list:
            if iter_discount_factor.tenor.label == tenorlabel.upper():
                return iter_discount_factor
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
                iter_capitalized_factor.get_discount_factor()
                for iter_capitalized_factor in self.fx_rate_list
            ], linearization)

    def get_capitalized_factor_by_maturity_date(
            self, maturity_date: datetime.date) -> cls_capitalized_factor:
        return self.discount_factor_curve.get_discount_factor_by_maturity_date(
            maturity_date).get_capitalized_factor()


class cls_swap_point_panel(cls_fx_rate_curve):
    def __init__(self,
                 primary_ccy: cls_currency=None,
                 currency_pair: cls_currency_pair=None,
                 fx_rate_list: list=None):
        fx_rate_list.sort(
            key=lambda fx_rate: fx_rate.tenor.maturity_date, reverse=False)

        self.currency_pair = currency_pair
        self.fx_rate_list = fx_rate_list
        super().__init__(primary_ccy, fx_rate_list)

    def set_swap_point_panel_by_df_curves(
            self,
            primary_ccy: cls_currency,
            currency_pair: cls_currency_pair,
            spot_rate_input: cls_fx_spot_rate,
            base_ccy_df_curve: cls_discount_factor_curve,
            und_ccy_df_curve: cls_discount_factor_curve):

        spot_rate = spot_rate_input.get_fx_rate_by_quotation(
            currency_pair.quotation)

        #base_t_s_df= cls_discount_factor()
        base_t_s_df = base_ccy_df_curve.get_discount_factor_by_maturity_date(
            spot_rate.tenor.maturity_date)

        #und_t_s_df= cls_discount_factor()
        und_t_s_df = und_ccy_df_curve.get_discount_factor_by_maturity_date(
            spot_rate.tenor.maturity_date)

        if primary_ccy.label == base_ccy_df_curve.currency.label:

            for iter_base_df in base_ccy_df_curve.fx_rate_list:

                iter_und_df = und_ccy_df_curve.get_discount_factor_by_maturity_date(
                    iter_base_df.tenor.maturity_date)

                iter_swap_point = cls_swap_point(currency_pair,
                                                 iter_base_df.tenor)
                iter_swap_point.set_swap_point_by_discount_factor(
                    spot_rate,
                    iter_base_df.get_remaining_df_by(base_t_s_df),
                    iter_und_df.get_remaining_df(und_t_s_df))
                self.fx_rate_list.append(iter_swap_point)

        elif primary_ccy.label == und_ccy_df_curve.currency.label:
            for iter_und_df in und_ccy_df_curve.fx_rate_list:

                iter_base_df = base_ccy_df_curve.get_discount_factor_by_maturity_date(
                    iter_und_df.tenor.maturity_date)

                iter_swap_point = cls_swap_point(currency_pair,
                                                 iter_und_df.tenor)
                iter_swap_point.set_swap_point_by_discount_factor(
                    spot_rate,
                    iter_base_df.get_remaining_df(base_t_s_df),
                    iter_und_df.get_remaining_df_by(und_t_s_df))
                self.fx_rate_list.append(iter_swap_point)
