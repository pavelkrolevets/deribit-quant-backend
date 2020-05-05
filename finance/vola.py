from __future__ import absolute_import
from delta_hedger.gateio import getVola
import gate_api
from delta_hedger.utils.deribit_api import RestClient
import time
from datetime import datetime
import json

def getHistVola(window, timeframe, instrument):
    # GATEIO API v.4
    configuration = gate_api.Configuration()
    configuration.key = '5f5430e6102ad1c31486b56ea7ab9c5c'
    configuration.secret = '3974ca809f6525f0c2bd5866e5fa44e28633a7e4983f707f698952bb10acd047'

    ''' GateIo part'''
    # create an instance of the API class
    api_spot = gate_api.SpotApi(gate_api.ApiClient(configuration))

    histVola = getVola(api_spot, 600, timeframe, (instrument+"_USDT"), window, False)
    # print(histVola)
    hist_vola_graph = []
    for i in range(24*7, len(histVola)):
        hist_vola_graph.append({'x': i, 'y': histVola["vola"].iloc[i]})

    # for index, row in histVola.iterrows():
    #     #     # print(row.name)
    #     hist_vola_graph.append({'x': int(row["Time"]), 'y': float(row["vola"])})
    return hist_vola_graph


def getImpliedVola(deribitKey, deribitSecret):
    '''Deribit Part'''
    deribitClient = RestClient(deribitKey, deribitSecret)
    index = deribitClient.index("BTC")
    print(index)
    ## check for open positions
    positions = deribitClient.positions()
    print("Open positions", positions)
