from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from db_helper import *
import json

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # def do_GET(self):
    #     logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
    #     self._set_response()
    #     self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        data = json.loads(post_data.decode('utf-8'))
        print(data)

        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), data)

        if data['email'] != None and data['stripe_cust_id'] != None \
                and data['created_at'] != None and data['invite_code'] != None:
            save_email(data['email'], data['stripe_cust_id'], data['invite_code'], data['created_at'])
            self._set_response()
            self.wfile.write("POST request for {} successfully completed".format(self.path).encode('utf-8'))
        else:
            print('ERROR request BODY')
            self._set_response()
            self.wfile.write("POST request for {} body error".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    print('server_address = ', server_address)
    try:
        print(httpd.server_address)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')
