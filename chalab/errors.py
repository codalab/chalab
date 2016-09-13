import logging
import traceback

from django.shortcuts import render

log = logging.getLogger('errors')


class HTTPException(Exception):
    status_code = None

    def __init__(self, template, message, long_message, **context):
        self.template = template
        self.message = message
        self.long_message = long_message
        self.context = context

    def render(self, request):
        context = {'message': self.message,
                   'long_message': self.long_message,
                   'status_code': self.status_code}
        context.update(self.context)

        return render(request, self.template, context=context, status=self.status_code)


class HTTP400Exception(HTTPException):
    status_code = 400


class ErrorHandlingMiddleware(object):
    def process_exception(self, request, exception):
        if not isinstance(exception, HTTPException):  # here you check if it yours exception
            log.error('Error: %s', request.path,
                      exc_info=traceback.format_exc(),
                      extra={'request': request})

        try:
            return exception.render(request)
        except AttributeError as e:
            return None
