class UnsetAcceptLanguageHeaderMiddleware(object):
    """
        Remove HTTP_ACCEPT_LANGUAGE header in order to use value
        defined in settings.py
    """

    def process_request(self, request):
       if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del(request.META['HTTP_ACCEPT_LANGUAGE'])
