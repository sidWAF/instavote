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
event_bridge_url = 'https://jlzje4iqm8.veo.endpoint.events.amazonaws.com'  # Replace 

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis
    
def publish_event(event_bus_name, event_detail_type, event_source, event_detail):
    # Initialize the EventBridge client
    client = boto3.client('events', region_name='us-east-1')

    # Construct the event
    event = {
        'DetailType': event_detail_type,
        'Source': event_source,
        'Detail': json.dumps(event_detail),
        'EventBusName': event_bus_name
    }

    # Publish the event
    response = client.put_events(Entries=[event])

    # Check the response
    if response['FailedEntryCount'] == 0:
        print("Event published successfully")
    else:
        print("Failed to publish event")


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
        if vote == "b":
            # trigger step-function
            print("triggering eventbridge")
            
            event_bus_name = 'default'
            event_detail_type = 'my.event.detail.type'
            event_source = 'customer_feedback'
            event_detail = {'Vote': 'B'}

            publish_event(event_bus_name, event_detail_type, event_source, event_detail)

            try:
                response = requests.post(event_bridge_url, json=event_detail)
                if response.status_code == 200:
                    print("Successfully sent event to EventBridge via HTTP POST")
                else:
                    print("Failed to send event. Status code: {response.status_code}")
            except Exception as e:
                print("Error sending event: {e}")

        
            
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
