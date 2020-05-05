from __future__ import absolute_import
from delta_hedger.gateio import getVola
import gate_api
from delta_hedger.delta_hedger import hedgeDelta
from delta_hedger.celery_app import celery_app
from celery.utils.log import get_task_logger
from delta_hedger.utils.deribit_api import RestClient
import time


logger = get_task_logger(__name__)

@celery_app.task(name='deltahedge.processing')
def start_delta_hedge(interval_min,interval_max, time_period, currency, instrument, deribit_key, deribit_secret):
    '''Deribit Part'''
    deribitClient = RestClient(deribit_key, deribit_secret)
    # print("Deribit client account", deribitClient.account(currency, True))
    index = deribitClient.index(currency)
    print("Index", index)
    # index = requests.get("https://test.deribit.com/api/v2/public/get_index?currency=ETH")
    # index = json.loads(index.content)

    # # GATEIO API v.4
    # configuration = gate_api.Configuration()
    # configuration.key = '5f5430e6102ad1c31486b56ea7ab9c5c'
    # configuration.secret = '3974ca809f6525f0c2bd5866e5fa44e28633a7e4983f707f698952bb10acd047'
    #
    # ''' GateIo part'''
    # # create an instance of the API class
    # api_spot = gate_api.SpotApi(gate_api.ApiClient(configuration))

    '''Run delta hedger'''
    if currency=="BTC":
        while True:
            # histVola = getVola(api_spot, 1000, '1h', 'BTC_USDT', 24 * 7, False)
            hedgeDelta(deribitClient, index['btc'], interval_min, interval_max, currency, instrument)
            time.sleep(time_period)
    elif currency=="ETH":
        while True:
            # histVola = getVola(api_spot, 1000, '1h', 'ETH_USDT', 24 * 7, False)
            hedgeDelta(deribitClient, index['eth'], interval_min, interval_max, currency, instrument)
            time.sleep(time_period)
