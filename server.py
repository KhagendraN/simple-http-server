#server.py

import socket
import os

# Define the host and port for the server
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
STATIC_DIR = 'static'

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request:\n{request}")

    # Parse the requested file from the request
    try:
        # Extract the requested file path
        request_line = request.splitlines()[0]
        requested_file = request_line.split()[1]
        if requested_file == '/':
            requested_file = '/index.html'  # Default to index.html

        # Build the full path to the requested file
        file_path = os.path.join(STATIC_DIR, requested_file.strip('/'))

        # Open and read the file
        with open(file_path, 'rb') as f:
            response_body = f.read()
            response_headers = 'HTTP/1.1 200 OK\r\n'
            content_type = 'text/html' if requested_file.endswith('.html') else 'text/css' if requested_file.endswith('.css') else 'application/javascript'
            response_headers += f'Content-Type: {content_type}\r\n'
            response_headers += 'Content-Length: {}\r\n'.format(len(response_body))
            response_headers += '\r\n'
            response = response_headers.encode() + response_body
    except FileNotFoundError:
        # Handle the case where the file is not found
        response = b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 Not Found</h1>'

    # Send the response back to the client
    client_socket.sendall(response)
    client_socket.close()

def run_server():
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Serving HTTP on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_request(client_socket)

if __name__ == '__main__':
    run_server()
