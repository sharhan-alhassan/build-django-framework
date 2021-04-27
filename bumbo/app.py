# app.py

from api import API

app = API()

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