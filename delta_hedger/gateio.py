import pandas as pd
import numpy  as np
from datetime import datetime
import matplotlib.pyplot as plt
import gate_api

# GATEIO API v.4
configuration = gate_api.Configuration()
configuration.key = '5f5430e6102ad1c31486b56ea7ab9c5c'
configuration.secret = '3974ca809f6525f0c2bd5866e5fa44e28633a7e4983f707f698952bb10acd047'


def getHistory(api_instance, frame, interval, currency_pair):

    # Market candlesticks
    history = api_instance.list_candlesticks(currency_pair, limit=frame, interval=interval)

    # convert to Pandas dataframe
    data = pd.DataFrame(np.array(history).reshape(frame, 6), columns=['Time', 'Volume', 'Open', 'High', 'Low', 'Close'])
    tmpList = []
    for i in data['Time']:
        tmpList.append(datetime.utcfromtimestamp(int(i)).strftime('%H:%M:%S'))
    data.index = tmpList
    data["Close"] = data["Close"].astype(float)
    data["Open"] = data["Open"].astype(float)
    data["High"] = data["High"].astype(float)
    data["Low"] = data["Low"].astype(float)
    return data

def getVola(api_instance, frame, interval, currency_pair, window, plot):

    # Market candlesticks
    history = api_instance.list_candlesticks(currency_pair, limit=frame, interval=interval)

    # convert to Pandas dataframe
    data = pd.DataFrame(np.array(history).reshape(frame, 6), columns=['Time', 'Volume', 'Open', 'High', 'Low', 'Close'])
    tmpList = []
    for i in data['Time']:
        tmpList.append(datetime.utcfromtimestamp(int(i)).strftime('%Y-%m-%d %H:%M:%S'))
    data.index = tmpList
    data["Close"] = data["Close"].astype(float)
    data["Open"] = data["Open"].astype(float)
    data["High"] = data["High"].astype(float)
    data["Low"] = data["Low"].astype(float)
    data['log_ret'] = np.log(data['Close'] / data['Close'].shift(1))

    vola_adj = 0

    if interval == '1m':
        vola_adj = np.sqrt(365* 24* 60)
    if interval == '1h':
        vola_adj = np.sqrt(365 * 24)
    if interval =='1d':
        vola_adj = np.sqrt(365)

    data['vola'] = data['log_ret'].rolling(window).std() * vola_adj

    if plot==True:
        """Plot result"""
        plt.plot(data['vola'])
        plt.grid(False)
        plt.xlabel('time step')
        plt.ylabel("level")
        plt.show()
    return data['vola']

if __name__ == '__main__':
    api_spot = gate_api.SpotApi(gate_api.ApiClient(configuration))
    vola = getVola(api_spot, 1000, '1h', 'ETH_USDT', 24*7, True)
    print(vola)
