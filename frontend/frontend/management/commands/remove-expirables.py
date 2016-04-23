import logging
from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.core.management.base import NoArgsCommand
from django.db import connection
from django.db.utils import OperationalError
from django.utils.timezone import now, timedelta

logger = logging.getLogger('django')


class Command(NoArgsCommand):
    help = 'Remove expired instances'

    def handle_noargs(self, *args, **kwargs):
        logger.info('Starting expired instances removal...')
        for app in apps.get_app_configs():
            if app.name not in settings.SCAPL_INSTALLED_APPS:
                continue
            for model in apps.get_app_config(app.label).get_models():
                # first, check if a field 'expires_after' exists
                try:
                    model._meta.get_field('expires_after')
                except FieldDoesNotExist:
                    logger.debug(' +--- no field \'expires_after\' in model \'{}\''.format(model.__name__))
                    continue
                # second, check if a field 'date_created' exists
                try:
                    model._meta.get_field('date_created')
                except FieldDoesNotExist:
                    logger.debug(' +--- no field \'date_created\' in model \'{}\''.format(model.__name__))
                    continue
                # now, remove expired instances
                del_count = 0
                try:
                    query_set = filter(lambda x: x.date_created <= now() - timedelta(seconds=x.expires_after), model.objects.all())
                    del_count = len(query_set)
                    for record in query_set:
                        record.delete()
                        logger.debug(' +--- deleted instance \'{}\' for model \'{}\''.format(model.__name__, str(record)))
                # just pass if such an error occurs, e.g. if the database was reset and an error occured at re-creation
                except OperationalError:
                    connection.close()  # in case of such error, the connection has to be gracefully closed
                logger.info('Deleted {} instances of model \'{}\''.format(del_count, model.__name__))
        logger.info('Expired instances removal done.')
