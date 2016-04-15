# -*- coding: UTF-8 -*-
from celery.task import task


"""
class DebugTask(Task):
    abstract = True

    def after_return(self, *args, **kwargs):
        print('Task returned: {0!r}'.format(self.request))
"""


@task
def generic(apl_id, item_id, call, args, nresults):
    return None
