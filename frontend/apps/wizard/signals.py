# -*- coding: UTF-8 -*-
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import Signal, receiver
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from frontend import celery_app
from importlib import import_module
from kombu import Connection
from kombu.compat import Publisher
from .models import TaskItemResult

smodels = import_module("apps.scheme.models")


def wizard_load_handler(sender, **kwargs):
    task_id, cmd, conn, routing = kwargs.get('task_id'), kwargs.get('cmd'), kwargs.get('conn'), kwargs.get('routing')
    if not all([task_id, cmd, conn, routing]):
        return _('Bad arguments')
    if routing not in settings.ROUTING_KEYS.keys():
        return _('Unexpected Data Item type')
    with Publisher(connection=conn, exchange="scapl", exchange_type="topic", routing_key=settings.ROUTING_KEYS[routing]) as pub:
        pub.send({
            'task': 'generic',
            'id': task_id,
            'args': (cmd, ),
            'retries': 0,
            'eta': str(now()),
            'expiration': settings.ASYNC_TASK_EXPIRATION,
        })


@receiver(pre_delete, sender=TaskItemResult)
def task_revoke_handler(sender, instance, **kwargs):
    task_id = str(instance)
    di = smodels.DataItem.objects.get_subclass(id=instance.task.item.id)
    if isinstance(di, smodels.SEDataItem):
        routing = 'search'
    elif isinstance(di, smodels.ASDataItem):
        routing = 'automation'
    else:
        return
    result = celery_app.AsyncResult(task_id)
    # it the task is not over yet, revoke and terminate it
    if not result.ready():
        celery_app.control.revoke(task_id, terminate=True)
    # then send a message with expiration 0 to ensure the result is dropped from the backend
    # NB: a method named 'forget' for the AsyncResult class exists but is not implemented yet for multiple backends
    with Connection(settings.BROKER_URL) as conn:
        with Publisher(connection=conn, exchange="scapl", exchange_type="topic", routing_key=settings.ROUTING_KEYS[routing]) as pub:
            pub.send({
                'task': 'generic',
                'id': task_id,
                'args': (None, ),
                'expiration': 0,
            })


wizard_load = Signal(providing_args=['task_id', 'cmd', 'conn', 'routing'])
wizard_load.connect(wizard_load_handler)
