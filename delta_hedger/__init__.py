from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from delta_hedger.celery_app import celery_app as celery_app
__all__ = ['celery_app']
