from celery import Celery
import time
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

celery = Celery('delta_hedger', broker='redis://localhost:6379/0')

logger = get_task_logger(__name__)

@celery.task(name='deltahedge.processing', bind=True, base=AbortableTask)
def start_delta_hedge(self):
    while not self.is_aborted():
        logger.info("Ping-Pong")
        time.sleep(5)

    logger.info("Task aborted.")

