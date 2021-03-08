from __future__ import absolute_import
from celery import Celery

celery_app = Celery('delta_hedger', include=['delta_hedger.tasks'])
celery_app.conf.broker_url = 'redis://localhost:6379/0'
celery_app.conf.result_backend = 'redis://localhost:6379/0'
celery_app.conf.task_track_started = True
# celery_app.conf.task_ignore_result = True
# celery_app.conf.task_store_errors_even_if_ignored = True

if __name__ == '__main__':
    celery_app.start()
