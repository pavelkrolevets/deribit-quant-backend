from __future__ import absolute_import
from celery import Celery
from celery.utils.log import get_task_logger


celery_app = Celery('delta_hedger')
celery_app.conf.broker_url = 'redis://localhost:6379/0'
celery_app.conf.result_backend = 'redis://localhost:6379/0'

logger = get_task_logger(__name__)
if __name__ == '__main__':
    celery_app.start()
