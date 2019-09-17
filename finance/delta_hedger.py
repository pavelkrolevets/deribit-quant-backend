from celery import Celery
import time
from celery.utils.log import get_task_logger

celery = Celery('delta_hedger')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'

logger = get_task_logger(__name__)

@celery.task(name='deltahedge.processing')
def start_delta_hedge():
    while True:
        logger.info("Ping-Pong")
        time.sleep(5)

