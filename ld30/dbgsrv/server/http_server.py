__author__ = 'Oliver Maskery'

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib.parse
import threading
import json


class SimpleHttpServer():
    def __init__(self, target, backend):
        self.server_thread = None
        self.server = ThreadedHTTPServer(target, HTTPRequestHandler, backend)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def wait_for_thread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.wait_for_thread()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def __init__(self, target, handler, backend):
        HTTPServer.__init__(self, target, handler)

        self.backend = backend

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class Response(object):

    def __init__(self, number=200, content_type='application/json'):
        self.number = number
        self.headers = [('Content-Type', content_type)]
        self.content = ''
        self.needs_encode = True

    def respond(self, handler):
        handler.send_response(self.number)
        for header in self.headers:
            handler.send_header(header[0], header[1])
        handler.end_headers()
        if self.needs_encode:
            content = self.content.encode()
        else:
            content = self.content
        handler.wfile.write(content)


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        api_base = "/api/v1/"

        parsed = urllib.parse.urlparse(self.path)
        unquoted_path = urllib.parse.unquote(parsed.path)
        path_parts = [part for part in unquoted_path.split("/") if part != '']

        if self.path.startswith(api_base):
            response = self.handle_api_request(path_parts[2:], unquoted_path)
        else:
            response = self.handle_web_request(path_parts, unquoted_path)

        response.respond(self)

    def handle_web_request(self, path, unquoted_path):
        white_list = [
            '/', '/index.html',
            '/css/main.css',
            '/js/main.js'
        ]

        if unquoted_path not in white_list:
            return Response(403)

        if unquoted_path == "/":
            unquoted_path = "/index.html"

        if unquoted_path.endswith(".htm"):
            unquoted_path += "l"

        base_path = "web"

        if unquoted_path.endswith(".html"):
            response = Response(content_type='text/html')
        elif unquoted_path.endswith(".js"):
            response = Response(content_type='application/javascript')
        elif unquoted_path.endswith(".css"):
            response = Response(content_type='text/css')
        else:
            return Response(404)

        try:
            handle = open(base_path + unquoted_path, 'rb')
            response.content = handle.read()
            response.needs_encode = False
        except IOError:
            return Response(404)

        return response

    def handle_api_request(self, path, unquoted_path):
        if len(path) < 1:
            return Response(404)

        front = path[0]

        if front != 'projects':
            return Response(404)

        if len(path) < 2:
            return self.list_projects()

        project_name = path[1]

        if project_name not in self.server.backend.projects.keys():
            return Response(404)

        if len(path) < 3:
            return Response(404)

        if path[2] != 'pages':
            return Response(404)

        if len(path) < 4:
            return self.list_pages(project_name)

        page_name = path[3]

        page = self.server.backend.projects[project_name].get_page(page_name)
        if page is None:
            return Response(404)

        if len(path) < 5:
            return Response(404)

        if path[4] != 'sections':
            return Response(404)

        if len(path) < 6:
            return self.list_sections(page)

        section_name = path[5]

        section = page.get_section(section_name)
        if section is None:
            return Response(404)

        if len(path) < 7:
            return Response(404)

        if path[6] != 'values':
            return Response(404)

        if len(path) < 8:
            return self.list_values(section)

        value_name = path[7]

        value = section.get_value(value_name)
        if value is None:
            return Response(404)

        return self.get_value(value)

    def list_projects(self):
        response = Response()

        blob = {
            'projects': [project_name for project_name in self.server.backend.projects.keys()]
        }

        response.content = json.dumps(blob)

        return response

    def list_pages(self, project_name):
        response = Response()

        blob = {
            'pages': [page.page_name for page in self.server.backend.projects[project_name].pages]
        }

        response.content = json.dumps(blob)

        return response

    def list_sections(self, page):
        response = Response()

        blob = {
            'sections': [section.section_name for section in page.sections]
        }

        response.content = json.dumps(blob)

        return response

    def list_values(self, section):
        response = Response()

        blob = {
            'values': [
                {
                    'value_name': value.value_name,
                    'value_type': value.value_type,
                    'value': value.value
                } for value in section.values
            ]
        }

        response.content = json.dumps(blob)

        return response

    def get_value(self, value):
        response = Response()

        blob = {
            'value_type': value.value_type,
            'value': value.value
        }

        response.content = json.dumps(blob)

        return response
