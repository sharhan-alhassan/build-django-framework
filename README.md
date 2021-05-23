
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Building Python Web Framework
## Part 1:
[Reference Material: From testdriven.io](https://testdriven.io/payments/python-web-framework/)

1. ### WSGI - Web Server Gateway Interface
The **Web Server:**
Serving clients requests as responses. WS takes requets, send it to the pythonApp, 'hey dude, a client needs this info'. Takes it and serves the client as response. WS knows nothing about the content or anything else.

    Client - Web Server - PythonApp

The **Web App** only exists at execution time and goes back to the sleep. Anytime there's a client's request, the Web Server wakes the Web App up and ask for the response to the request, the Web App performs its execution, serves the response and goes back to sleep

The above is problematic. Waking the PythonApp up and sending requests for response all the time on way. What about if the request was in different languages.

### WSGI to the Rescue:
`WSGI:` Is basically a set of rules on how a Web Server should/communicate with an Application

    client -> Web Server -> WSGI -> PythonApp

According to [PEP 333](https://www.python.org/dev/peps/pep-0333/#the-application-framework-side), the document that specifies the details of `WSGI`, the `application interface` is implemented as a callable object such as a function, a method, a class or an instance with a `__call__` method. This object takes `2 positional arguments` and return the `response body` as strings in an iterable. The two arguments are:

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

### What are handlers in Python?
Handlers take the general form of function:

    handler(request, response):
        ...

Basically, they are functions that handle certain events that they are registered for [github answer](https://stackoverflow.com/questions/58628653/what-are-handlers-in-python-in-plain-english)

They are functions that are called when certain events happen

    @app.route('/home')
    def home(request, response):
        reponse.text = "Hello, World"
    
`home` function is a handler that gives the message `Hello World` when the url `/home` is called. 

After creating your routes and associating them with the necessary handlers, you would realized that if you make a request to a non-existing route, you'll get a: `Internal Server Error`. Back in the console you'll get a message like: `TypeError: 'NoneType' object is not callable`.

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


### Parameterized
This is to say to add additional parameters to the route. Eg; something like `/home/{your_name}/`. An extra parameter of `your_name` can be taken. There's a package called [Parse](https://pypi.org/project/parse/). It is the opposite of `format()`

Example: Open python and try this

    >>> from parse import parse
    >>> result = parse("Hello {name}", "Hello, Sam")
    >>> print(result.named)
    {'name': 'Sam'}

`Hello, Sam` was able to identify that `Sam` corresponds to the provided `{name}`

Now apply the `parse` to the `find_handler` method

### Duplicate routes and Class-based handlers
Currently if you add mutiple routes, the framework will recognize and will not throw out an error but rather return the last route.
Take the two routes and handlers as an example:

    @app.route('/about')
    def about(request, response):
        response.text = "This is First About page"

    @app.route('/about')
    def about2(request, response):
        response.text = "This is Second About page"

The above two routes all have the same route name but with different content. So if you go to `http://localhost/about`, guess which response will be displayed? The the second handler, `about2` will be served. The framework will not not complain which is problematic. 

### The new solution: resolving routing duplicates
We want to do the following
1. First check if the route exists and throw an excepting that it already exists if the user tries to add a duplicate route handler. Using python dict will easily help us check if a given path already exists in the dictionary. 
2. If the route doesn't exist, then we can add it to our route dictionary. 

    Solution: Change the `route` method so that it throws an exception if an existing route is being added again. 

    def route(self, path):
        if path in self.routes:
            raise AssertionError("Such route already exists.")
            
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

Or we can refactor the code to look like this:

    def route(self, path):
        assert path not in self.routes, "Such route already exists." # new
            
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper

### Classe-based Handlers
Class based handlers are cooler and elegant for larger projects to maintain. Let's create one `class-based handler`

Now, after adding  `class based handlers`. We need to go to the `handler_request` method and check to see if the handler is a `function based handler` and serve it as such or if it's `class based handler` depending on the request method, if `GET` we call the `get()` method of the class and if request method is `POST`, we call the `post()` method of the class. 
If the handler is a class based handler, we can use the built-in `inspect` module to check it first before.

Our `handle_request` method now looks like this:

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        # New
        if handler is not None:     
            if inspect.isclass(handler):
                pass # class-based handler here
            else:
                handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response

Most important thing: if a classed-based handler is used, it is important to know and find the appropriate method of the class based on the given request method. Is it `GET` or `POST`. The built-in `getattr` function can be used to find the request method of the class based handler.

Now refactoring the `handler_request` method:

    if inspect.isclass(handler):
        handler_function = getattr(handler(), request.method.lower(), None)
        pass

`getattr()`: 
    1. accepts an object instance as first parameter
    2. accepts the attribute name as second parameter
    3. the third argument is the value to return if nothing is found

Therefore, `GET` will return get, `POST` will return post. `random_attribute` will return `None`. If the `handler_function` is `None`, it means such function was not implemented in the class and the request method is not allowed. If the `handler_function` is not None, then call it

    if inspect.isclass(handler):
        handler_function = getattr(handler(), request.method.lower(), None)
        if handler_function is None:
            raise AttributeError("Method not allowed", request.method)
        handler_function(request, response, **kwargs)

Now we can combine the `handler_function` with the `handler` to have a clear code.

Old code:   

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler_function = getattr(handler(), request.method.lower(), None)
                if handler_function is None:
                    raise AttributeError("Method not allowed", request.method)
                handler_function(request, response, **kwargs)
            else:
                handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response

Refactored code:

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

You can test the class based handler by going to: `http://localhost:8000/book`. You will get the page with the message `Books Page`

You can test the class based handler for the `POST` method by this on the console: `curl -X POST http://localhost:8000/book`. You will get the page with the message `Endpoint to create a book`


### Unit Tests
We're going to introduce `unit tests` with `pytest` and add test client so we can start testing the endpoints. 

Packages required for the `tests` section of this part

    pip install pytest
    pip install requests
    pip install requests-wsgi-adapter
    pip install pytest-cov

### Test Client:
This is a way of testing the API without spinning up a server. 

### Test coverage

- `pytest-cov`: pytest coverage is a measure used to describe the degree to which the `source code` of a program is executed when a particular `test suite` runs. High test coverage means, high lower chance of source code containing undetected `bugs`

- Add `.coveragerc` file which is used for the configuration of the coverage tool to ignore the `venv virtual environment` directory along with the `test_bumbo.py`, `conftest.py` and `app.py` files. 

- Put the following code in the `.coveragerc` file

    [run]
    omit = venv/*,test_bumbo.py,conftest.py,app.py

- Run the command to run the tests coverage:

`pytest --cov=. test_bumbo.py`

### Django-Like Routes and Templates


### Jinja2
Jinja2 uses a central object called the template `Environment`. You will configure this environment upon application initialization and load templates with the help of this environment.

Here's an example of how to create and configure a new `Environment`:

    import os 
    from jinja2 import Environemnt, FileSystemLoader

    template_env = Environment(loader=FileSystemLoader(os.path.abspath("templates")))

-  In the `api.py` of the `template` method, you'd notice `context=None`.

- This should be fairly straightforward, right? The only thing you may be wondering about is why I gave context a default value of None, checked if it is None, and then set the value to an empty dictionary, {}? Why not just give it a default value of {} in the declaration? Well, dict is a mutable object and it is a bad practice to set a mutable object as a default value in Python. You can read more about this [here](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments). This is an excellent, and frequently asked, interview question for Pythonistas.


### Middleware:
- Basically, middleware is a component that can modify an HTTP request and/or response and is designed to be chained together to form a pipeline of behavioral changes during request processing. Examples of middleware tasks are request logging and HTTP authentication. The main point is that neither of these are fully responsible for responding to a client. Instead, each middleware changes the behavior in some way as part of the pipeline, leaving the actual response to come from something later in the pipeline. In our case, that something which actually responds to a client is our request handlers. Middlewares are wrappers around our WSGI app that have the ability to modify requests and responses.

- From the bird's eye view, the code will look like this:

    FirstMiddleware(SecondMiddlware(our_wsgi_app))

- So, when a request comes in, it hits `FirstMiddleware` first, which modifies the request in some way and sends it over to `SecondMiddleware`. `SecondMiddleware` then modifies the request and sends it over to `our_wsgi_app`. The app handles the request, prepares the response and sends it back to `SecondMiddleware`. It can modify the response if it wants before sending it back to `FirstMiddleware`. The response is modified again, and then `FirstMiddleware` sends it back to the web server `(e.g., Gunicorn)`.