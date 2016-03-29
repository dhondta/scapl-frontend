#!/usr/bin/env python
import os
import sys
from django.conf import settings
from django.core.management import execute_from_command_line


# TODO: [optional] collect app names instead of providing a flat list
APPS = ['common', 'profiles', 'scheme', 'wizard']


def fail_silently(args, msg=None):
    print("{}: ".format(args[-1])),
    try:
        execute_from_command_line(args)
    except:
        if isinstance(msg, str):
            print(msg)


def migrate_apps_then_run(apps=APPS, load_data=True):
    for app in apps:
        execute_from_command_line([sys.argv[0], "makemigrations", app])
    execute_from_command_line([sys.argv[0], "migrate"])
    if load_data:
        dir = settings.SMUGGLER_FIXTURE_DIR
        for fn in sorted([f for f in os.listdir(dir) if f.endswith('.json')]):
            fail_silently([sys.argv[0], "loaddata", "-i", os.path.join(dir, fn)], "No fixture loaded")
    sys.argv[1] = "runserver"
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings.dev")

    if sys.argv[1] == "draw_models":
        execute_from_command_line([sys.argv[0], "graph_models", "-a", "-g", "-o", "scapl-frontend-models.png"])
    elif sys.argv[1] == "reset-and-run":
        try:
            os.remove("./scapl.sqlite3")
        except OSError:  # if the DB was already removed, simply pass
            pass
        migrate_apps_then_run()
    elif sys.argv[1] == "migrate-and-run":
        migrate_apps_then_run(load_data=False)
    else:
        execute_from_command_line(sys.argv)

"""
django-extensions:

 :export_mails: e.g. with '--format=google google.csv', generates a list of emails from all users
 :graph_models: with '-a -o myapp_models.png', generates a graphviz graph of app models
 :runserver_plus: enhanced runserver
 :shell_plus: enhanced shell
 :show_urls: produces a tab-separated list of (url_pattern, view_function, name) tuples
 :validate_templates: checks templates for rendering errors

"""
