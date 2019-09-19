from __future__ import absolute_import
from celery import Celery

celery_app = Celery('delta_hedger', include=['delta_hedger.tasks'])
celery_app.conf.broker_url = 'redis://localhost:6379/0'
celery_app.conf.result_backend = 'redis://localhost:6379/0'

if __name__ == '__main__':
    celery_app.start()
