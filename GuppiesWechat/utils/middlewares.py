import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse, HttpRequest


class ProcessCORSMiddleware(object):

    def add_cors_header(self, origin, response):
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response[
            'Access-Control-Allow-Headers'] = 'reqid, nid, host, x-real-ip, x-forwarded-ip, event-type, event-id, accept, content-type'

    def process_request(self, request):
        request._dont_enforce_csrf_checks = True  # For csrf
        if request.method == 'OPTIONS':
            response = HttpResponse(status=204)
            self.add_cors_header(request.META.get('HTTP_ORIGIN'), response)
            return response

    def process_response(self, request, response):

        if request.META.get('HTTP_ACCEPT') == 'application/json':
            self.add_cors_header(request.META.get('HTTP_ORIGIN'), response)
        return response


class ExceptionMiddleware(object):
    def process_exception(self, request, exception):

        if request.META.get('CONTENT_TYPE') == 'application/json':
            logging.exception(exception)
            if isinstance(exception, ObjectDoesNotExist):
                return JsonResponse({}, status=404)
            return JsonResponse({}, status=500)
