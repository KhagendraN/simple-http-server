import socket
import subprocess
import os

HOST = socket.gethostbyname(socket.gethostname())
#HOST = "0.0.0.0"
PORT = 5050
STATIC_DIR = 'static'

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request:\n{request}")

    try:
        request_line = request.splitlines()[0]
        requested_file = request_line.split()[1]

        if requested_file == '/':
            requested_file = '/index.html'

        if requested_file == '/chat':
            response = handle_chat_message(request)
        else:
            file_path = os.path.join(STATIC_DIR, requested_file.strip('/'))
            response = serve_static_file(file_path)

    except FileNotFoundError:
        response = b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 Not Found</h1>'
    except Exception as e:
        response = f'HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>Internal Server Error: {str(e)}</h1>'.encode()

    client_socket.sendall(response)
    client_socket.close()

def handle_chat_message(request):
    try:
        message = request.split('\r\n\r\n')[1]
        
        # Here, we could simulate a romantic response
        # Example: If the message contains certain words, return a romantic reply
        if "hello" in message.lower():
            response_message = "Oh, hello my dear! How can I make your day more wonderful?❤️"
        # elif "love" in message.lower():
        #     response_message = "I feel like my heart just skipped a beat! ❤️"
        else:
            # Default response from Ollama chatbot
            result = subprocess.check_output(['ollama', 'run', 'samantha-mistral', message])
            response_message = result.decode("utf-8").strip()

        response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{{"message": "{response_message}"}}'.encode()

    except subprocess.CalledProcessError as e:
        response = f'HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>Error while processing message: {e.output.decode("utf-8")}</h1>'.encode()
    except Exception as e:
        response = f'HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>Internal Server Error: {str(e)}</h1>'.encode()

    return response

def serve_static_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            response_body = f.read()
            response_headers = 'HTTP/1.1 200 OK\r\n'
            content_type = 'text/html' if file_path.endswith('.html') else 'text/css' if file_path.endswith('.css') else 'application/javascript'
            response_headers += f'Content-Type: {content_type}\r\n'
            response_headers += f'Content-Length: {len(response_body)}\r\n'
            response_headers += '\r\n'
            response = response_headers.encode() + response_body
    except FileNotFoundError:
        response = b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>404 Not Found</h1>'
    return response

def run_server():
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
