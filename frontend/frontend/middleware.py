from django.conf import settings
from django.core.exceptions import PermissionDenied


class RemoteAddrMiddleware(object):
    """ Ensure REMOTE_ADDR is set with client IP """
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
            request.META['REMOTE_ADDR'] = ip


class FilterIPMiddleware(object):
    """ Check if client IP is not blacklisted """
    def process_request(self, request):
        denied_ips = settings.DENIED_HOSTS
        ip = request.META.get('REMOTE_ADDR')
        if ip in denied_ips:
            raise PermissionDenied
        return None
