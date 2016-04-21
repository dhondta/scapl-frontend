from django.core.management import call_command
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'Draw SCAPL\'s models'

    def handle(self, *args, **options):
        call_command('graph_models', all_applications=True, group_models=True, outputfile='scapl-frontend-models.png')
