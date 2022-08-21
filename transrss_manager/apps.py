import logging
import os
import sys
import re
from django.apps import AppConfig
from crontab import CronTab, current_user
from transrss.settings import BASE_DIR
SUBSCRIBER_INVERVAL = (lambda x: int(x[0]) if x is not None else 600)(re.match("\d+", os.getenv('SUBSCRIBER_INVERVAL', '600')))
SUBSCRIBER_ENV = {
    'DJANGO_SUPERUSER_USERNAME': os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
    'DJANGO_SUPERUSER_PASSWORD': os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
}
logger = logging.getLogger(__name__)

class TransrssManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transrss_manager'
    subscriber_cron_comment = 'rss_subscriber'

    def ready(self) -> None:
        if 'runserver' not in sys.argv:
            return
        ''' Start the subscriber` process
        '''
        if os.getenv("SUBSCRIBER_MODE", "ON") != 'OFF':
            logger.info("Start subscriber.")
            subscriber_path = BASE_DIR / self.name / "subscriber.py"
            django_cron = CronTab(current_user())
            django_cron.remove_all(comment=self.subscriber_cron_comment)
            job_env = " ".join([f"{key}={value}" for key, value in SUBSCRIBER_ENV.items()])
            job = django_cron.new(command=f"{job_env} {sys.executable} {subscriber_path} 1> /dev/stdout 2> /dev/stderr", comment=self.subscriber_cron_comment)
            job.minute.every(int(SUBSCRIBER_INVERVAL / 60))
            django_cron.write()
            logger.info("Write cron job:", job)
    
