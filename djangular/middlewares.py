
class DjangularUrlMiddleware(object):
    """
    If the view is djangular's url reverser, return the response immediately, omitting middleware processing.
    Since result of middleware processing depends on view function running through the middlewares with djangular
    url reverser view would yield incorrect results. Returning a response immediately ensures that no middlewares were
    ran. The url reverser view decorates the actual view function with middlewares, so they're then ran through with
    the correct view.
    This must be the first middleware in the MIDDLEWARE_CLASSES tuple!
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        is_reverser = getattr(callback, 'djng_url_reverser', False)
        if is_reverser:
            return callback(request, *callback_args, **callback_kwargs)
        return None