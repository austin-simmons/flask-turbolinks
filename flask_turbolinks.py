from urlparse import urlparse
from flask import request, session


__all__ = ('turbolinks', 'same_origin')


def turbolinks(app):

    @app.before_request
    def turbolinks_referer():
        referer = request.headers.get('X-XHR-Referer')
        if referer:
            request.referer = referer

    @app.after_request
    def turbolinks_response(response):
        if request.method != 'GET':
            response.set_cookie('request_method', request.method)

        if 'Location' in response.headers:
            # this is a redirect response
            loc = response.headers['Location']
            session['_turbolinks_redirect_to'] = loc

            # cross domain redirect
            referer = request.headers.get('X-XHR-Referer')
            if referer and not same_origin(loc, referer):
                response.status_code = 403
        else:
            if '_turbolinks_redirect_to' in session:
                loc = session.pop('_turbolinks_redirect_to')
                response.headers['X-XHR-Redirected-To'] = loc
        return response


def same_origin(current_uri, redirect_uri):
    parsed_uri = urlparse(current_uri)
    if not parsed_uri.scheme:
        return True
    parsed_redirect = urlparse(redirect_uri)

    if parsed_uri.scheme != parsed_redirect.scheme:
        return False

    if parsed_uri.hostname != parsed_redirect.hostname:
        return False

    if parsed_uri.port != parsed_redirect.port:
        return False
    return True
