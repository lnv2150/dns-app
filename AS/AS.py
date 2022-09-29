import socket
import pickle
import os
import json
import time
import logging as log

log.basicConfig(format='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
                datefmt='%I:%M:%S %p',
                level=log.DEBUG)

ip_host = "0.0.0.0"
buffer_size = 1024
auth = "/tmp/auth_db.json" 
serverport = 53533

def main():
    udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsocket((ip_host, serverport))

    log.info(f"UDP is server up and UDP server is listening on "
             f"{socket.gethostbyname(socket.gethostname())}:{serverport}")

    while (True):
        bytes_message, address_client = udpsocket.recvfrom(buffer_size)
        small_msg = pickle.loads(bytes_message)
        log.info(f"Message from Client: {small_msg!r}")
        

        if len(small_msg) == 2:
	    dns_type, dns_name = small_msg
            with open(auth, "r") as f:
                records = json.load(f)

            if dns_name not in records:
                log.info(f"No DNS record found for {dns_name}")
                dns_record = None

            dns_value, dns_ttl_ts, dns_ttl = records[dns_name]
            log.debug(f"DNS records for {dns_name}: {records[dns_name]} found")
            log.debug(f"Current time={time.time()} dns_ttl_ts={dns_ttl_ts}")
            if time.time() > dns_ttl_ts:
                log.info(f"TTL expired for {dns_name}")
                dns_record = None
            dns_record =  (dns_type, dns_name, dns_value, dns_ttl_ts, dns_ttl)
            if dns_record:
                (_, dns_name, dns_value, _, dns_ttl) = dns_record
                response_exp = ("A", dns_name, dns_value, dns_ttl)
            else:
                response_exp = ""
            response_bytes = pickle.dumps(response_exp)
            udpsocket.sendto(bytes_message, address_client)
           
        elif len(small_msg) == 4:
	    dns_name, dns_value, dns_type, dns_ttl = pickle.loads(bytes_message)
	    dns_ttl_ts = time.time() + int(dns_ttl)
            if not os.path.exists(auth):
                with open(auth, "w") as f:
                    json.dump({}, f, indent=4)

            with open(auth, "r") as f:
                records = json.load(f)


            records[dns_name] = (dns_value, dns_ttl_ts, dns_ttl)

            with open(auth, "w") as f:
                json.dump(records, f, indent=4)
                log.debug(f"DNS record for {dns_name} {(dns_value, dns_ttl_ts, dns_ttl)} is saved")
            
        else:
            small_msg = f"Expected msg of len 2 or 4, got :{small_msg!r}"
            log.error(small_msg)
            udpsocket.sendto(small_msg, address_client)


if __name__ == '__main__':
    log.info("Spinning up authoritative server")
    main()