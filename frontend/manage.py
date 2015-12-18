#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings")

    from django.core.management import execute_from_command_line

    if sys.argv[1] == "demonstration":
        execute_from_command_line([sys.argv[0], "makemigrations", "frontend"])
        execute_from_command_line([sys.argv[0], "syncdb", "--noinput"])
        execute_from_command_line([sys.argv[0], "migrate", "frontend"])
        execute_from_command_line([sys.argv[0], "runserver"])
    elif sys.argv[1] == "migrate":
        execute_from_command_line([sys.argv[0], "syncdb", "--noinput"])
        execute_from_command_line(sys.argv)
    elif sys.argv[1] == "runserver":
        # execute_from_command_line([sys.argv[0], "loaddata", "./data/initial.json"])
        execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)