import os
import time

from dateutil import tz

from datetime import datetime


def sprint(string, *args, **kwargs):
    """Safe Print (handle UnicodeEncodeErrors on some terminals)"""
    try:
        print(string, *args, **kwargs)
    except UnicodeEncodeError:
        string = string.encode('utf-8', errors='ignore') \
            .decode('ascii', errors='ignore')
        print(string, *args, **kwargs)


def print_title(title):
    """Helper function to print titles to the console more nicely"""
    sprint('\n')
    sprint('=={}=='.format('=' * len(title)))
    sprint('= {} ='.format(title))
    sprint('=={}=='.format('=' * len(title)))


def get_env(name, message, cast=str):
    """"" Helper to get environment variables interactively """
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e)
            time.sleep(1)


def en_to_ar_num(number):
    number_string = str(number)
    lis = []
    dic = {
        '0': '۰',
        '1': '١',
        '2': '٢',
        '3': '۳',
        '4': '٤',
        '5': '۵',
        '6': '٦',
        '7': '۷',
        '8': '۸',
        '9': '۹',
    }

    for char in number_string:
        if char in dic:
            lis.append(dic[char])
        else:
            lis.append(char)
    return "".join(lis)


def ar_to_en_num(number):
    number_string = str(number)
    lis = []
    dic = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
    }

    for char in number_string:
        if char in dic:
            lis.append(dic[char])
        else:
            lis.append(char)
    return "".join(lis)


def utc_to_local(utc_datetime):
    to_zone = tz.tzlocal()

    return utc_datetime.astimezone(to_zone)


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or utc_to_local(datetime.now())
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    # else: # crosses midnight
    #     return check_time >= begin_time or check_time <= end_time


