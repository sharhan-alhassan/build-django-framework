# app.py

from api import API

app = API()

@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(resquest, response):
    response.text = "Hello from the ABOUT page"