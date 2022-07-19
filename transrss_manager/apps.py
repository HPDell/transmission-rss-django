import logging
import os
import sys
from multiprocessing import Process
from django.apps import AppConfig
from transrss_manager.subscriber import feed_subscribe


class TransrssManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transrss_manager'

    def ready(self) -> None:
        if 'runserver' not in sys.argv:
            return
        ''' Start the subscriber` process
        '''
        if os.getenv("SUBSCRIBER_MODE", "ON") != 'OFF':
            logging.info("Start subscriber.")
            subscriber_process = Process(target=feed_subscribe)
            subscriber_process.daemon = True
            subscriber_process.start()
