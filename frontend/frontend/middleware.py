import re
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


"""
Tightens up response content by removed superflous line breaks and whitespace.
By Doug Van Horn

---- CHANGES ----
v1.1 - 31st May 2011
Cal Leeming [Simplicity Media Ltd]
Modified regex to strip leading/trailing white space from every line, not just those with blank \n.

---- TODO ----
* Ensure whitespace isn't stripped from within <pre> or <code> or <textarea> tags.

"""


class StripWhitespaceMiddleware(object):
    """ Strips leading and trailing whitespace from response content
     See: https://code.djangoproject.com/wiki/StripWhitespaceMiddleware """
    def __init__(self):
        self.whitespace = re.compile('^\s*\n', re.MULTILINE)
        # self.whitespace_lead = re.compile('^\s+', re.MULTILINE)
        # self.whitespace_trail = re.compile('\s+$', re.MULTILINE)

    def process_response(self, request, response):
        if "text" in response['Content-Type']:
            if hasattr(self, 'whitespace_lead'):
                response.content = self.whitespace_lead.sub('', response.content)
            if hasattr(self, 'whitespace_trail'):
                response.content = self.whitespace_trail.sub('\n', response.content)
            # Uncomment the next line to remove empty lines
            if hasattr(self, 'whitespace'):
                response.content = self.whitespace.sub('', response.content)
            return response
        else:
            return response
