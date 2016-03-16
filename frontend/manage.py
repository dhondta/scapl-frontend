#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings.dev")

    from django.core.management import execute_from_command_line

    if sys.argv[1] == "migrate-and-run":
        execute_from_command_line([sys.argv[0], "makemigrations"])
        execute_from_command_line([sys.argv[0], "migrate"])
        sys.argv[1] = "runserver"
        execute_from_command_line(sys.argv)
    elif sys.argv[1] == "migrate":
        execute_from_command_line([sys.argv[0], "migrate", "--run-syncdb"])
        execute_from_command_line(sys.argv)
    elif sys.argv[1] == "runserver":
        # execute_from_command_line([sys.argv[0], "loaddata", "./data/initial.json"])
        execute_from_command_line(sys.argv)
    elif sys.argv[1] == "draw_models":
        execute_from_command_line([sys.argv[0], "graph_models", "-a", "-g", "-o", "scapl-frontend-models.png"])
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
