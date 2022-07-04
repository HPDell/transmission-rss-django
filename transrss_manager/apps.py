from multiprocessing import Process
import os
from django.apps import AppConfig
from .subscriber import feed_subscribe


class TransrssManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transrss_manager'
    ''' Start the subscriber process
    '''
    if os.getenv("SUBSCRIBER_MODE") != 'OFF':
        subscriber = Process(target=feed_subscribe)
        subscriber.daemon = True
        subscriber.start()
