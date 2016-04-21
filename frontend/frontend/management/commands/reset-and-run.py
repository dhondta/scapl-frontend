import logging
import os
import shutil
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Reset DB, migrate project\'s applications, load fixtures then run the server'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', help='Optional port number, or ipaddr:port')
        parser.add_argument('--reset-on-reload', action='store_true', dest='reload', default=False,
                            help='Also apply reset-and-run at auto-reload')

    def handle(self, addrport, **kwargs):
        if kwargs.get('reload') or os.environ.get('RUN_MAIN') != 'true':
            call_command('remove-expirables')
            for db_file in [x['NAME'] for x in settings.DATABASES.values()]:
                try:
                    os.remove(db_file)
                    logger.info("Removed {}".format(db_file))
                except OSError:  # if the DB was already removed, simply pass
                    pass
            for app in apps.get_app_configs():
                if app.name in settings.SCAPL_INSTALLED_APPS:
                    try:
                        shutil.rmtree(os.path.join('./apps', app.label, 'migrations'))
                        logger.info("Removed migrations of app '{}'".format(app.label))
                    except OSError:
                        pass
        # In auto-reload mode, migrations will be re-made and the server will be reloaded (fixtures are not reloaded)
        for app in apps.get_app_configs():
            if app.name in settings.SCAPL_INSTALLED_APPS:
                call_command('makemigrations', app.label)
        call_command('migrate')
        try:
            executor = MigrationExecutor(connections[DEFAULT_DB_ALIAS])
            executor.migration_plan(executor.loader.graph.leaf_nodes())
        except:
            return
        if kwargs.get('reload') or os.environ.get('RUN_MAIN') != 'true':
            dir = settings.SMUGGLER_FIXTURE_DIR
            for fn in sorted([f for f in os.listdir(dir) if f.endswith('.json')]):
                fixture = os.path.join(dir, fn)
                print("{}, ".format(fixture)),
                try:
                    call_command('loaddata', fixture, ignorenonexistent=True)
                except Exception as e:
                    print("No fixture loaded")
                    if isinstance(e, TypeError):
                        logger.warning("   +---> Please refer to 'BUGFIX' in the 'data' folder for this kind of error")
                    else:
                        with open(fixture) as f:
                            if f.read().strip(" \n[]") == "":
                                logger.warning("   +---> This fixture is emtpy")
        call_command('runserver', addrport)
