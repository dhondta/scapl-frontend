# -*- coding: UTF-8 -*-
from django.contrib.messages.storage.session import SessionStorage
from itertools import chain


class AvoidDuplicateMessageMixin(object):
    def add(self, level, message, extra_tags):
        messages = chain(self._loaded_messages, self._queued_messages)
        for m in messages:
            if m.message == message:
                return
        return super(AvoidDuplicateMessageMixin, self).add(level, message, extra_tags)


class CustomMessageStorage(AvoidDuplicateMessageMixin, SessionStorage):
    pass
