

## Building Python Web Framework
## Part 1:
[Reference Material: From testdriven.io](https://testdriven.io/payments/python-web-framework/)

1. ### WSGI - Web Server Gateway Interface
The **Web Serber:**
Serving clients requests as responses. WS takes requets, send it the pythonApp, 'hey dude, a client needs this info'. Takes it and serves the client as response. WS knows nothing about the content or anything else.
    Client - Web Server - PythonApp

The **Web App** only exists at execution time and goes back to the sleep. Anytime there's a client's request, the Web Server wakes the Web App up and ask for the response to the request, the Web App performs its execution, serves the response and goes back to sleep

The above is problematic. Waking the PythonApp up and sending requests for response all the time on way. What about if the request was in different languages.

### WSGI to the Rescue:
`WSGI:` Is basically a set of rules on how a Web Server should/communicate with an Application
    client -> Web Server -> WSGI -> PythonApp

According to PEP [PEP 333](https://www.python.org/dev/peps/pep-0333/#the-application-framework-side), the document that specifies the details of `WSGI`, the `application interface` is implemented as a callable object such as a function, a method, a class or an instance with a `__call__` method. This object takes `2 positional arguments` and return the `response body` as strings in an iterable. The two arguments are:
    1. A `dictionary with environment variables` 
    2. A callback function that will be used to send HTTP statuses and HTTP headers to the server

### Middleware
*Middleware changes things a bit. With middleware, the above scenario will look like this:*

    1. The web server gets a request.
    2. Now, instead of talking directly to PythonApp, it will send it through a postman (e.g., middleware).
    3. The postman delivers the request to PythonApp.
    4. After PythonApp does his job, it gives the response to the postman.
    5. The postman then delivers the response to the web server.

The only thing to note is that while the postman is delivering the request/response, it may tweak it a little bit.

## Requests and Routing
The following will be built:
    1. The request handlers(think Django views)
    2. Routing -- both simple(like `/books/`) and parameterized (like `/books/{id}/`)

`Gunicorn:` Is a WSGI-compatible light-weight application server. Like WSGI, you need a callable object(function, method, class) that expects two parameters(`environ` and `start_response`) and returns an `iterable response` or response_body

### Start creating a framework
1. Create the name/folder of the framework(eg;bumbo)
2. Create a virtual environment and activate it: `virtualenv venv`
3. Create a file, `app.py`
4. Create a simple web

    def app(environ, start_response):
        response_body = b"Hello, World"
        status = '200 OK'
        start_response(status, headers=[])
        return iter([response_body])

5. Install gunicorn: `pip install gunicorn`
6. Start/run the app: `gunicorn app:app`
    Explanation of the above command:
    The first `app` on the left: Is the file you created, `app.py`.
    The second `app` on the right: Is the function you just wrote, `def app(...):`

There is a cool package called [WebOb](https://pypi.org/project/WebOb/) that provides classes for `HTTP` `requests` and `responses` by wrapping the `WSGI` request environment and response status, headers, and body. By using this package, we can pass the `environ` and `start_response` to the classes, which are provided by this provided by this package, and not have to deal with them ourselves. 

### Install Webob
Import `Request` and `Response` classes at the beginning of the `api.py` file.
We can use the `request` to get the `user_agent` info from it. At the same time, we can refactor the response creation into its own method called `handle_request`. This handle_request will then be called in the `__call__` function as a response to display the `user_agent`


## Routing
All requests are handle the same way using the the `handle_request` method. We need to make it dynamic to server requests from different routs such as `/home/` and `/about/`

Create the about functions in `app.py` and associate them with the mentioned paths: `/home/` and `/about/`:

    from api import API
    app = API()

    @app.route('/home')
    def home(request, response):
        response.text = "Hello from the HOME page"

    @app.route('/about')
    def about(resquest, response):
        response.text = "Hello from the ABOUT"

**NB: The `route` method is a decorator that accepts a path and wraps the methods.**

Put this code in the `api.py` file:

    class API:
        def __init__(self):
            self.routes = {}
        ...

        def route(self, path):
            def wrapper(handler):
                self.routes[path] = handler
                return handler
            return wrapper

In the `__init__` method, you define a `dict` and called `self.routes` where the framework will store `paths` as `keys` and `handlers` as `values`. The values of that `dict` will look something like this:

    {
        '/home': <function home at 0x1100a34>,
        '/about': <function about at 0x1155ad3>
    }

The in the  `route` method, you take a path as an argument and in the `wrapper` method, you add this path in the `self.routes` dictionary as a key and the handler as a value

After creating your routes and associating them with the needed handlers, you would realized that if you make a request to a non-existing route, you'll get a: `Internal Server Erro`. Back in the console you'll get a message like: `TypeErro: 'NoneType' object is not callable`.

Let's create a method that returns a simple `HTTP response` of `Not Found` with a `404 status` code:

    # api.py
    class API:
        ...
        def default_response(self, response):
            response.status_code = 404
            response.text = "Not Found"

Add this piece of code to the `handle_request` method:

    class API:
        ...
        def handle_request(self, request):
            response = Response()
            for path, handler in self.routes.items():
                if path == request.path:
                    handler(request, response)
                    return response
            self.default_response(response)
            return response 