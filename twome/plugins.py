
def entitle(title):
    """
    Decorator that sets tiddlyweb.title in environ.
    """
    def entangle(f):
        def entitle(environ, start_response, *args, **kwds):
            output = f(environ, start_response)
            environ['tiddlyweb.title'] = title
            return output
        return entitle
    return entangle


def do_html():
    """
    Decorator that makes sure we are sending text/html.
    """
    def entangle(f):
        def do_html(environ, start_response, *args, **kwds):
            output = f(environ, start_response)
            start_response('200 OK', [
                ('Content-Type', 'text/html; charset=UTF-8')
                ])
            return output
        return do_html
    return entangle


def require_role(role):
    """
    Decorator that requires the current user has role ADMIN.
    """
    def entangle(f):
        def require_role(environ, start_response, *args, **kwds):
            admin = role in environ['tiddlyweb.usersign']['roles']
            if admin:
                return f(environ, start_response)
            else:
                raise(UserRequiredError, 'insufficient permissions')
        return require_role
    return entangle


