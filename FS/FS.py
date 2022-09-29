from flask import Flask, request
import socket
import pickle
import logging as log


app = Flask(__name__)

@app.route('/')
def introduction_FS():
    return "This is Fibonacci Server (FS)"

def fiboancci_number(n):
    if n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    elif n < 0:
        raise ValueError("n should be greater than 0")
    else:
        return fiboancci_number(n - 1) + fiboancci_number(n - 2)


@app.route('/fibonacci')
def fibonacci():
    n = int(request.args.get('number'))
    return str(fiboancci_number(n))


@app.route('/register', methods=['PUT'])
def register():
    body = request.json
    if not body:
        raise ValueError("body is None") 
    IPFS    = body["fs_ip"]
    IPAS    = body["as_ip"]
    PORTAS  = body["as_port"]
    ttl      = body["ttl"]
    small_msg = pickle.dumps(((body["hostname"], IPFS, "A", ttl)))
    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(small_msg, (IPAS, PORTAS))
    return "Registration Successful!"

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9090,
            debug=True)