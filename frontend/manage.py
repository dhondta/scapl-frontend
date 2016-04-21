#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings.dev")

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
