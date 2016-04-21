import logging
import os
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Migrate project\'s applications then run the server'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', help='Optional port number, or ipaddr:port')
        parser.add_argument('--load-fixtures', action='store_true', dest='fixtures', default=False,
                            help='Load fixtures from SMUGGLER_FIXTURE_DIR set in project\'s settings')

    def handle(self, addrport, **kwargs):
        # In auto-reload mode, migrations will be re-made and the server will be reloaded (fixtures are not reloaded)
        for app in apps.get_app_configs():
            if app.name in settings.SCAPL_INSTALLED_APPS:
                call_command('makemigrations', app.label, interactive=False)
        call_command('migrate')
        try:
            executor = MigrationExecutor(connections[DEFAULT_DB_ALIAS])
            executor.migration_plan(executor.loader.graph.leaf_nodes())
        except Exception as e:
            logger.error("Something failed with migrations execution")
            for l in str(e).split():
                logger.error(l)
            return
        if os.environ.get('RUN_MAIN') != 'true' and kwargs.get('fixtures'):
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
