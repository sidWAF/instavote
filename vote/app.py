from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import boto3

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
        print(vote)
        if vote == 'b':
            # trigger step-function
            print("Triggering step function")
            SFN.Client.start_execution(**kwargs)
            stateMachineARN = "arn:aws:states:us-east-1:279824249008:execution:EventBridgeStateMachine-SjJIEbJXZNTq:baac59d9-b1e4-4019-a7a3-ef971ae0fd46"
            response = client.start_execution(
                stateMachineArn = stateMachineARN,
                name='newEventExecution',
                input='Vote is B',
                traceHeader='something'
            )
            
        print(data)

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
