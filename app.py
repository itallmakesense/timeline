import requests
from sanic import Sanic
from sanic.response import json


IP_API = "http://ip-api.com/json"


app = Sanic()


@app.route('/')
async def root(request):
    response = requests.get(f"{IP_API}/{request.ip}")
    return json(response.json())

if __name__ == '__main__':
    app.run()
