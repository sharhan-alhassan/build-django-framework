# app.py

from api import API

app = API()

# function based handlers
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

# class based handler
@app.route('/book')
class BookResource:
    def get(self, req, resp):
        resp.text = "Books Page."

    def post(self, req, resp):
        resp.text = "Endpoint to create a book."

@app.route('/book/{id:d}/update')
class PutBook:
    def put(self, req, resp, id):
        resp.text = f"Book with id: {id} modified!"

@app.route('/book/{id:d}/delete')
class DeleteBook:
    def delete(self, req, resp, id):
        resp.text = f"Book with id: {id} deleted!"