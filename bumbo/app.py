# app.py

from api import API
from middleware import Middleware

app = API()


# function based handlers --Flask-like routes
@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(resquest, response):
    response.text = "Hello from the ABOUT page"

@app.route('/about/{name}')
def greeting(request, response, name):
    response.text = f"Hello, {name}"

@app.route('/tell/{age:d}')
def get_age(request, response, age):
    response.text = f"I am {age} years old"

# templates handler
@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "index.html",
        context = {"title": "Awesome Framework", "name": "Bumbo"}
    ).encode()

@app.route('/exception')
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be used")

# exception handler 
def custom_exception_handler(request, response, exception_cls):
    response.txt = str(exception_cls)

app.add_exception_handler(custom_exception_handler)



# Django-like handlers
def handler(req, resp):
    resp.text = "sample"

app.add_route("/sample", handler)


# class-based handlers
@app.route('/book')
class BookResource:
    def get(self, req, resp):
        resp.text = "Books Page."

    def post(self, req, resp):
        resp.text = "Endpoint to create a book."

@app.route('/book/{id:d}/update')
class PutBook:
    def put(self, req, resp, id):
        resp.text = f"Book with id {id} is modified!"

@app.route('/book/{id:d}/delete')
class DeleteBook:
    def delete(self, req, resp, id):
        resp.text = f"Book with id {id} is deleted!"


# simpple custom middleware
class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def procss_response(self, req, res):
        print("Processing response", req.url)

app.add_middleware(SimpleCustomMiddleware)

