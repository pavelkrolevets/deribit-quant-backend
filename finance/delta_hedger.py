from celery import Celery
import time
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
celery = Celery(broker='redis://localhost:6379/0')

@celery.task(name='deltahedge.processing')
def start_delta_hedge():
    while True:
        logger.info("Ping-pong")
        time.sleep(5)
