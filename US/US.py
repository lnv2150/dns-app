from flask import Flask, request
import logging as log
import pickle
import socket
import requests
import socket


app = Flask(__name__)

@app.route('/')
def introduction_US():
    return 'This is User Server - US'


@app.route('/fibonacci', methods=["GET"])
def fibonacci_number():
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = request.args.get('hostname').replace('"','')
    number   = int(request.args.get('number'))
    IPAS    = request.args.get('as_ip').replace('"','')
    socket_udp.sendto(pickle.dumps(("A", hostname)), (IPAS, int(request.args.get('as_port'))))
    response, _ = socket_udp.recvfrom(2048)
    response = pickle.loads(response)
    type, hostname, fs_ip, ttl = response
    if not fs_ip:
        return "Not able to retrieve fs_ip"
    return requests.get(f"http://{fs_ip}:{int(request.args.get('fs_port'))}/fibonacci",
                        params={"number": number}).content


app.run(host='0.0.0.0',
        port=8080,
        debug=True)
