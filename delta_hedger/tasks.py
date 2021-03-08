from __future__ import absolute_import
from delta_hedger.gateio import getVola
import gate_api
from delta_hedger.delta_hedger import hedgeDelta
from delta_hedger.celery_app import celery_app
from celery.utils.log import get_task_logger
from delta_hedger.utils.deribit_api import RestClient
import time


logger = get_task_logger(__name__)

@celery_app.task(name='deltahedge.processing', max_retries=5)
def start_delta_hedge(delta, time_period, currency, instrument, deribit_key, deribit_secret):
    try:
        '''Deribit Part'''
        deribitClient = RestClient(deribit_key, deribit_secret)
        # print("Deribit client account", deribitClient.account(currency, True))
        index = deribitClient.index(currency)
        print("Index", index)

        '''Run delta hedger'''
        if currency=="BTC":
            while True:
                # histVola = getVola(api_spot, 1000, '1h', 'BTC_USDT', 24 * 7, False)
                hedgeDelta(deribitClient, index['btc'], delta, currency, instrument)
                time.sleep(time_period)
        elif currency=="ETH":
            while True:
                # histVola = getVola(api_spot, 1000, '1h', 'ETH_USDT', 24 * 7, False)
                hedgeDelta(deribitClient, index['eth'], delta, currency, instrument)
                time.sleep(time_period)
    except subprocess.CalledProcessError as er:
        self.update_state(state='FAILURE', meta={'exc': er})