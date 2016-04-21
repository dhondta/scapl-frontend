import os
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Remove expirable model instances then run the server'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', help='Optional port number, or ipaddr:port')

    def handle(self, addrport, **kwargs):
        if os.environ.get('RUN_MAIN') != 'true':
            call_command('remove-expirables')
        call_command('runserver', addrport)
