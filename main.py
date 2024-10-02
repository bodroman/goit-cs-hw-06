from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing import Process
from pymongo import MongoClient
import json
import os
import datetime

# MongoDB setup
client = MongoClient('mongodb://mongodb:27017/')
db = client['chat_db']
messages_collection = db['messages']

class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        base_path = os.getcwd()  # Отримання поточного робочого каталогу
        if self.path == '/':
            self.path = os.path.join(base_path, 'index.html')
        elif self.path == '/message.html':
            self.path = os.path.join(base_path, 'message.html')
        elif self.path == '/style.css':
            self.path = os.path.join(base_path, 'style.css')
        elif self.path == '/logo.png':
            self.path = os.path.join(base_path, 'logo.png')
        else:
            self.send_error(404, 'File Not Found')
            self.path = os.path.join(base_path, 'error.html')

        return super().do_GET()


    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = dict([field.split('=') for field in post_data.split('&')])
            form_data['date'] = str(datetime.datetime.now())
            
            # Sending data to socket server
            with socket(AF_INET, SOCK_STREAM) as sock:
                sock.connect(('localhost', 5000))
                sock.sendall(json.dumps(form_data).encode('utf-8'))
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Message sent successfully!")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run_http_server():
    server_address = ('', 3000)
    httpd = ThreadedHTTPServer(server_address, MyRequestHandler)
    print("HTTP server running on port 3000")
    httpd.serve_forever()

def run_socket_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('localhost', 5000))
    server_socket.listen(5)
    print("Socket server running on port 5000")

    while True:
        conn, addr = server_socket.accept()
        data = conn.recv(1024).decode('utf-8')
        if data:
            message_data = json.loads(data)
            # Insert into MongoDB
            messages_collection.insert_one(message_data)
            print(f"Message received and stored: {message_data}")
        conn.close()

if __name__ == '__main__':
    http_process = Process(target=run_http_server)
    socket_process = Process(target=run_socket_server)

    http_process.start()
    socket_process.start()

    http_process.join()
    socket_process.join()
