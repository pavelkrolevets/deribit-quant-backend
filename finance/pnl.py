from math import log, sqrt, exp
from scipy import stats
from numpy import *
from time import time
from finance.option_bsm import call_option, put_option
from delta_hedger.utils.deribit_api import RestClient
from datetime import datetime, timedelta
import json

def compute_global_pnl(deribitKey, deribitSecret, range_min, range_max, step, risk_free, vola):
    '''Deribit Part'''
    deribitClient = RestClient(deribitKey, deribitSecret)
    index = deribitClient.index("BTC")
    print(index)
    ## check for open positions
    positions = deribitClient.positions()
    print("Open positions", positions)

    pnl = []

    for i in range(range_min, range_max, step):
        print("Range",i)
        pos_sum = 0
        for position in positions:
            instrument = position['instrument'].split('-')

            if position['kind'] == 'option':
                now = datetime.now()
                expiration = datetime.strptime(instrument[1], '%d%b%y')
                T = (expiration - now).seconds/(365*24*60*60)
                if instrument[3] == "C":
                    call = call_option(S0=i/i, K=int(instrument[2])/i, T=T, r=risk_free, sigma=vola)
                    pos_sum += call.value() * float(position['size']) * i - float(position['averagePrice']) * float(position['size']) * i

                if instrument[3] == "P":
                    put = put_option(S0=i, K=int(instrument[2]), T=T, r=risk_free, sigma=vola)
                    pos_sum += put.value() * float(position['size']) - float(position['averagePrice']) * float(position['size']) * i

            if position['kind'] == 'future':
                pos_sum += float(position['sizeBtc']) * i - float(position['sizeBtc']) * float(position['averagePrice'])


        pnl.append({'x':i, 'y':pos_sum})

    pnl_at_exp = []

    for i in range(range_min, range_max, step):
        pos_sum = 0
        for position in positions:
            instrument = position['instrument'].split('-')

            if position['kind'] == 'option':
                if instrument[3] == "C":
                    call = call_option(S0=i/i, K=int(instrument[2])/i, T=0.00001, r=risk_free, sigma=vola)
                    pos_sum += call.value() * position['size'] * i- float(position['averagePrice']) * float(position['size']) * i

                if instrument[3] == "P":
                    put = put_option(S0=i, K=int(instrument[2]), T=0.0001, r=risk_free, sigma=vola)
                    pos_sum += put.value() * float(position['size']) - float(position['averagePrice']) * float(position['size']) * i

            if position['kind'] == 'future':
                pos_sum += float(position['sizeBtc']) * i - float(position['sizeBtc']) * float(position['averagePrice'])

        pnl_at_exp.append({'x':i, 'y':pos_sum})

    return pnl, pnl_at_exp


def analize_positions(deribitKey, deribitSecret, positions, range_min, range_max, step, risk_free, vola):
    '''Deribit Part'''
    deribitClient = RestClient(deribitKey, deribitSecret)
    index = deribitClient.index("BTC")
    print(index)

    pnl = []

    for i in range(range_min, range_max, step):
        print("Range", i)
        pos_sum = 0
        for position in positions:
            instrument = position['instrument'].split('-')

            if position['kind'] == 'option':
                now = datetime.now()
                expiration = datetime.strptime(instrument[1], '%d%b%y')
                T = (expiration - now).seconds/(365*24*60*60)
                if instrument[3] == "C":
                    call = call_option(S0=i/i, K=int(instrument[2])/i, T=T, r=risk_free, sigma=vola)
                    pos_sum += call.value() * float(position['size']) * i - float(position['averagePrice']) * float(position['size']) * i

                if instrument[3] == "P":
                    put = put_option(S0=i, K=int(instrument[2]), T=T, r=risk_free, sigma=vola)
                    pos_sum += put.value() * float(position['size']) - float(position['averagePrice']) * float(position['size']) * i

            if position['kind'] == 'future':
                pos_sum += float(position['sizeBtc']) * i - float(position['sizeBtc']) * float(position['averagePrice'])


        pnl.append({'x':i, 'y':pos_sum})

    pnl_at_exp = []

    for i in range(range_min, range_max, step):
        pos_sum = 0
        for position in positions:
            instrument = position['instrument'].split('-')

            if position['kind'] == 'option':
                if instrument[3] == "C":
                    call = call_option(S0=i/i, K=int(instrument[2])/i, T=0.00001, r=risk_free, sigma=vola)
                    pos_sum += call.value() * position['size'] * i- float(position['averagePrice']) * float(position['size']) * i

                if instrument[3] == "P":
                    put = put_option(S0=i, K=int(instrument[2]), T=0.0001, r=risk_free, sigma=vola)
                    pos_sum += + put.value() * float(position['size']) - float(position['averagePrice']) * float(position['size']) * i

            if position['kind'] == 'future':
                pos_sum += float(position['sizeBtc']) * i - float(position['sizeBtc']) * float(position['averagePrice'])

        pnl_at_exp.append({'x':i, 'y':pos_sum})

    return pnl, pnl_at_exp
