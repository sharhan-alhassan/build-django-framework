
import pytest
from api import API

def test_custom_exeption_handler(api, client):
    def on_exception(req, resp, exc):
        resp.text = "AttributeErrorHappend"

    api.add_exception_handler(on_exception)

def test_template(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.body = api.template(
            "index.html", 
            context={"title": "Some Title", "name": "Some Name"}
        ).encode()

        response = client.get("http://testserver/html")

        assert "text/html" in response.headers["Content-Type"]
        assert "Some Title" in response.text
        assert "Some Name" in response.text

        
def test_basic_route_adding(api):
    @api.route('/home')
    def home(req, resp):
        resp.text = "YOLO"

def test_route_overlap_throws_exception(api):
    @api.route('/home')
    def home2(req, resp):
        resp.text = "YOLO"

def test_bumbo_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "THIS IS COOL"

    @api.route('/hey')
    def cool(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/hey").text == RESPONSE_TEXT

def test_parameterized_route(api, client):
    @api.route('/{name}')
    def hello(req, resp, name):
        resp.text = f"Hey, {name}"

    assert client.get("http://testserver/sam").text == "Hey, sam"
    assert client.get("http://testserver/dada").text == "Hey, dada"

def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not Found"

#*********** test class-based handlers *********************#
def test_class_based_handler_get(api, client):
    response_text = "This is a get request"

    @api.route('/book')
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text
    
    assert client.get('http://testserver/book').text == response_text

def test_class_based_handler_post(api, client):
    response_text = "This is is a post request"

    @api.route('/book')
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text
    
    assert client.post('http://testserver/book').text == response_text

def test_class_based_handler_not_allowed_method(api, client):
    @api.route('/book')
    class BookResource:
        def post(self, req, resp):
            resp.text = "yolo"

    with pytest.raises(AttributeError):
        client.get('http://testserver/book')