# api.py

import inspect

from webob import Request, Response
from parse import parse
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

class API:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        if path in self.routes:
            raise AssertionError("Such route already exists.")

        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)
        return response(environ, start_response)

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError("Method not allowed", request.method)
            handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response
         
    def default_response(self, response):
        response.status_code = 404
        response.text = "Not Found"

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session




        
# class API:
#     def __call__(self, environ, start_response):
#         request = Request(environ)

#         response = Response()
#         response.text = "Hello, World!"

#         return response(environ, start_response)


# class API:
#     def __call__(self, environ, start_response):
#         response_body = b"Hello, World!"
#         status = '200 OK'
#         start_response(status, headers=[])
#         return iter([response_body])

        