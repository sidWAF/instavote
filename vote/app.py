from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import boto3
import requests

option_a = os.getenv('OPTION_A', "Yes")
option_b = os.getenv('OPTION_B', "No")
hostname = socket.gethostname()
version = 'v1'

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis.rpush('votes', data)
        # Define the API Gateway endpoint URL
        if vote == "b":
            api_gateway_url = "https://asrkwkn73h.execute-api.us-east-1.amazonaws.com/MyStage/event"

            # Define your custom message payload
            custom_message = {
                'Vote': 'B'
            }

            # Convert payload to JSON string
            payload = json.dumps(custom_message)
            # Make a POST request to the API Gateway endpoint
            response = requests.post(api_gateway_url, data=payload)

            # Check response
            #print(response.status_code)
            print(response.text)


    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
        version=version,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
