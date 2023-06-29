import datetime

import pandas as pd
import holidays

current_year = datetime.date.today().year
last_three_years = range(current_year-2, current_year+1)
catalonia_holidays = holidays.country_holidays('ES', subdiv='CT', years=last_three_years)
holidays_calendar = catalonia_holidays


def get_dataframe():
    return pd \
        .read_csv('consumption.csv',
                  sep=';', decimal=',', parse_dates=['Fecha'], dayfirst=True) \
        .rename(columns={"Fecha": "date", "Hora": "hour", "AE_kWh": "kwh"}) \
        .drop(columns=['CUPS', 'AS_KWh', 'AE_AUTOCONS_kWh', 'REAL/ESTIMADO'])


def is_valley_usage(usage):
    return is_holiday_day(usage.date) or 0 < usage.hour <= 8


def is_holiday_day(date):
    return is_weekend(date) or is_bank_holiday(date)


def is_labour_day(date):
    return not is_holiday_day(date)


def is_weekend(date):
    return date.day_of_week in holidays_calendar.weekend


def is_bank_holiday(date):
    return date in holidays_calendar


def is_plain_usage(usage):
    return is_labour_day(usage.date) and (
        8 < usage.hour <= 10 or
        14 < usage.hour <= 18 or
        22 < usage.hour <= 24
    )


def is_peak_usage(usage):
    return is_labour_day(usage.date) and (
        10 < usage.hour <= 14 or
        18 < usage.hour <= 22
    )


if __name__ == '__main__':
    usages = get_dataframe()

    # See README.md for references of when valley, plain and peak rates apply
    usages_valley = usages[usages.apply(is_valley_usage, axis=1)]
    usages_plain = usages[usages.apply(is_plain_usage, axis=1)]
    usages_peak = usages[usages.apply(is_peak_usage, axis=1)]

    print("Total usages: %f kWh" % usages.kwh.sum())

    total_valley_kwh = usages_valley.kwh.sum()
    print("Total valley: %f kWh" % total_valley_kwh)

    total_plain_kwh = usages_plain.kwh.sum()
    print("Total plain: %f kWh" % total_plain_kwh)

    total_peak_kwh = usages_peak.kwh.sum()
    print("Total peak: %f kWh" % total_peak_kwh)

    print("Total valley+plain+peak: %f kWh" % (total_valley_kwh + total_plain_kwh + total_peak_kwh))
