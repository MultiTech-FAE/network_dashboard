from flask import Flask, jsonify, request, render_template
from paho.mqtt import client as mqtt

from static.py.mqtt_utils import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mqtt_messages')
def mqtt_messages():
    return render_template('mqtt_messages.html')


@app.route('/downlink')
def downlink():
    return render_template('downlinks.html')


@app.route('/connect', methods=['POST'])
def connect():
    global mqtt_client, broker_ip
    data = request.json
    broker_ip = data['broker']
    port = int(data['port'])
    topic = data['topic']

    if mqtt_client is not None:
        mqtt_client.disconnect()

    mqtt_client = mqtt.Client(userdata={'topic': topic})
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker_ip, port, 60)
    mqtt_client.loop_start()

    return jsonify({"message": "Connected to MQTT broker"})


@app.route('/send_downlink', methods=['POST'])
def send_downlink_route():
    data = request.json
    response, status_code = send_downlink(data)
    return jsonify(response), status_code


if __name__ == '__main__':
    app.run(debug=True, port=5000)
