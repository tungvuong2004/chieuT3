from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os
import json
from datetime import datetime
from cgi import FieldStorage

class EnhancedHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_file('index.html', 200)
        elif self.path.startswith('/static/'):
            self.serve_file(self.path.lstrip('/'), 200)
        elif self.path.startswith('/uploads/'):
            self.serve_file(self.path.lstrip('/'), 200)
        else:
            self.serve_404()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/chat':
            self.handle_chat_submission()
        elif self.path == '/upload':
            self.handle_file_upload()
        elif self.path == '/clear':
            self.clear_chat_history()

    def handle_chat_submission(self):
        """Handle chat message submission."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        post_params = parse_qs(post_data)
        username = post_params.get('username', ['Anonymous'])[0]
        message = post_params.get('message', [''])[0]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        os.makedirs('data', exist_ok=True)
        chat_file = os.path.join('data', 'chat.json')
        messages = []

        if os.path.exists(chat_file):
            with open(chat_file, 'r') as file:
                messages = json.load(file)

        messages.append({'username': username, 'message': message, 'time': timestamp})
        with open(chat_file, 'w') as file:
            json.dump(messages, file)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def handle_file_upload(self):
        """Handle file uploads."""
        form = FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        file_field = form['file']

        if file_field.filename:
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', file_field.filename)
            with open(file_path, 'wb') as output_file:
                output_file.write(file_field.file.read())

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def clear_chat_history(self):
        """Clear chat history by removing all messages."""
        chat_file = os.path.join('data', 'chat.json')
        if os.path.exists(chat_file):
            with open(chat_file, 'w') as file:
                json.dump([], file)  # Clear the file by overwriting it with an empty list
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def serve_file(self, filename, status_code):
        """Serve static files and inject dynamic content."""
        try:
            file_path = os.path.join(os.getcwd(), filename)
            if filename.endswith('.html'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                if filename == 'index.html':
                    content = content.replace("{{chat_messages}}", self.generate_chat_messages())
                    content = content.replace("{{uploaded_files}}", self.generate_uploaded_files())
                self.send_response(status_code)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                with open(file_path, 'rb') as file:
                    content = file.read()
                self.send_response(status_code)
                self.send_header('Content-Type', self.get_mime_type(filename))
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.serve_404()

    def generate_chat_messages(self):
        """Generate HTML for chat messages."""
        chat_file = os.path.join('data', 'chat.json')
        if not os.path.exists(chat_file):
            return "<p>No messages yet. Start the conversation!</p>"

        with open(chat_file, 'r') as file:
            messages = json.load(file)

        chat_html = "<ul>"
        for msg in messages:
            username = msg.get('username', 'Anonymous')
            message = msg.get('message', 'No message provided')
            time = msg.get('time', 'Unknown time')
            chat_html += f"<li><strong>{username}:</strong> {message} <span class='timestamp'>({time})</span></li>"
        chat_html += "</ul>"
        return chat_html

    def generate_uploaded_files(self):
        """Generate HTML for uploaded files."""
        upload_dir = os.path.join('uploads')
        if not os.path.exists(upload_dir):
            return "<p>No files uploaded yet.</p>"

        files_html = "<ul>"
        for filename in os.listdir(upload_dir):
            file_url = f"/uploads/{filename}"
            files_html += f'<li><a href="{file_url}" target="_blank">{filename}</a></li>'
        files_html += "</ul>"
        return files_html

    def get_mime_type(self, filename):
        """Get the MIME type of a file."""
        if filename.endswith('.html'):
            return 'text/html'
        elif filename.endswith('.css'):
            return 'text/css'
        elif filename.endswith('.js'):
            return 'application/javascript'
        elif filename.endswith('.png'):
            return 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            return 'image/jpeg'
        elif filename.endswith('.gif'):
            return 'image/gif'
        elif filename.endswith('.pdf'):
            return 'application/pdf'
        else:
            return 'application/octet-stream'

    def serve_404(self):
        """Serve a 404 Not Found response."""
        self.send_response(404)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>404 Not Found</h1><p>The page you requested does not exist.</p></body></html>")

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 8000
    server_address = (host, port)
    print(f"Starting server at http://{host}:{port}")
    httpd = HTTPServer(server_address, EnhancedHTTPRequestHandler)
    httpd.serve_forever()
