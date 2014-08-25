__author__ = 'Oliver Maskery'

import asyncore
import socket
import json


class Server(asyncore.dispatcher):

    def __init__(self, target):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(target)
        self.listen(10)

        self.projects = {}

        self.handlers = {
            'connect': self.handle_connect_message,
            'get-page': self.handle_get_page,
            'add-section': self.handle_add_section,
            'get-section': self.handle_get_section,
            'add-value': self.handle_add_value,
            'get-value': self.handle_get_value,
            'set-value': self.handle_set_value,
        }

    def remove_project(self, project):
        del self.projects[project.project_name]

    def handle_accepted(self, sock, address):
        print("[%s] connection established" % address[0])
        Connection(self, sock, address)

    def handle_connect_message(self, client, command, arguments):
        if 'project_name' not in arguments.keys():
            client.send_response(command, error="no project name specified")
            return
        if 'persist' not in arguments.keys():
            arguments['persist'] = False
        project_name = arguments['project_name']
        persists = bool(arguments['persist'])

        if project_name not in self.projects.keys():
            self.projects[project_name] = Project(project_name, persists)
            print("[%s] project created: %s (persists=%s)" % (client.address[0], project_name, persists))
        else:
            self.projects[project_name].update_persistence(persists)
            print("[%s] project connected: %s (persists=%s)" % (client.address[0], project_name, persists))

        client.project = self.projects[project_name]

        client.send_response(command, success=True)

    def handle_get_page(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        page_name = arguments['page']

        page = client.project.get_page(page_name)
        if page is None:
            client.send_response(command, error="unable to create/fetch requested page")
            return

        client.send_response(command, success=True)

    def handle_add_section(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        if 'section' not in arguments.keys():
            client.send_response(command, error="no section name specified")
            return
        page_name = arguments['page']
        section_name = arguments['section']

        page = client.project.get_page(page_name, create=False)

        if page is None:
            client.send_response(command, error="specified page does not exist")
            return

        section = page.add_section(section_name)
        if section is None:
            client.send_response(command, error="unable to create section")

        print("[%s] added section %s to page %s in project %s" % (client.address[0], section_name, page_name,
                                                                  client.project.project_name))
        client.send_response(command, success=True)

    def handle_get_section(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        if 'section' not in arguments.keys():
            client.send_response(command, error="no section name specified")
            return
        page_name = arguments['page']
        section_name = arguments['section']

        page = client.project.get_page(page_name, create=False)

        if page is None:
            client.send_response(command, error="specified page does not exist")
            return

        section = page.get_section(section_name)
        if section is None:
            print("[%s] added section %s to page %s in project %s" % (client.address[0], section_name, page_name,
                                                                      client.project.project_name))
            section = page.add_section(section_name)

        if section is None:
            client.send_response(command, error="unable to fetch/create section")
            return

        client.send_response(command, success=True)

    def handle_add_value(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        if 'section' not in arguments.keys():
            client.send_response(command, error="no section name specified")
            return
        if 'value_name' not in arguments.keys():
            client.send_response(command, error="no value name specified")
            return
        if 'value_type' not in arguments.keys():
            client.send_response(command, error="no value type specified")
            return
        if 'value' not in arguments.keys():
            client.send_response(command, error="no value specified")
            return
        page_name = arguments['page']
        section_name = arguments['section']
        value_name = arguments['value_name']
        value_type = arguments['value_type']
        value = arguments['value']

        page = client.project.get_page(page_name, create=False)
        if page is None:
            client.send_response(command, error="no page with that name exists")
            return

        section = page.get_section(section_name)
        if section is None:
            client.send_response(command, error="no section with that name exists")
            return

        new_value = section.add_value(value_name, value_type, value)
        if new_value is None:
            client.send_response(command, error="unable to create value")
            return

        client.send_response(command, success=True)

    def handle_set_value(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        if 'section' not in arguments.keys():
            client.send_response(command, error="no section name specified")
            return
        if 'value_name' not in arguments.keys():
            client.send_response(command, error="no value name specified")
            return
        if 'value' not in arguments.keys():
            client.send_response(command, error="no value specified")
            return
        page_name = arguments['page']
        section_name = arguments['section']
        value_name = arguments['value_name']
        new_value = arguments['value']

        page = client.project.get_page(page_name, create=False)
        if page is None:
            client.send_response(command, error="no page with that name exists")
            return

        section = page.get_section(section_name)
        if section is None:
            client.send_response(command, error="no section with that name exists")
            return

        value = section.get_value(value_name)
        if value is None:
            client.send_response(command, error="no value with that name exists")
            return

        value.set(new_value)

        client.send_response(command, success=True)

    def handle_get_value(self, client, command, arguments):
        if 'page' not in arguments.keys():
            client.send_response(command, error="no page name specified")
            return
        if 'section' not in arguments.keys():
            client.send_response(command, error="no section name specified")
            return
        if 'value_name' not in arguments.keys():
            client.send_response(command, error="no value name specified")
            return
        if 'value_type' not in arguments.keys():
            client.send_response(command, error="no value type specified")
            return
        if 'value' not in arguments.keys():
            client.send_response(command, error="no value specified")
            return
        page_name = arguments['page']
        section_name = arguments['section']
        value_name = arguments['value_name']
        value_type = arguments['value_type']
        value = arguments['value']

        page = client.project.get_page(page_name, create=False)
        if page is None:
            client.send_response(command, error="no page with that name exists")
            return

        section = page.get_section(section_name)
        if section is None:
            client.send_response(command, error="no section with that name exists")
            return

        value_obj = section.get_value(value_name)
        if value_obj is None:
            value_obj = section.add_value(value_name, value_type, value)
            if value_obj is None:
                client.send_response(command, error="unable to fetch/create value")
                return

        client.send_response(command, success=True)

    def handle_blob(self, client, blob):
        if 'cmd' not in blob.keys():
            client.send_response(None, error="no command specified")
            return
        if 'args' not in blob.keys():
            client.send_response(blob['cmd'], error="no args dictionary specified")

        command = blob['cmd']
        arguments = blob['args']

        if command not in self.handlers.keys():
            client.send_response(command, error="unknown command specified")
        else:
            handler = self.handlers[command]
            handler(client, command, arguments)


class Connection(asyncore.dispatcher_with_send):

    def __init__(self, server, sock, address):
        asyncore.dispatcher_with_send.__init__(self, sock)

        self.project = None

        self.address = address
        self.server = server
        self.buf = ''

    def handle_read(self):
        self.buf += self.recv(2048).decode()
        while True:
            end = self.buf.find("\n")
            if end == -1:
                break

            data = self.buf[:end]
            self.buf = self.buf[end+1:]

            blob = json.loads(data)

            self.server.handle_blob(self, blob)

    def handle_close(self):
        self.close()

        if self.project is not None and not self.project.persists:
            self.server.remove_project(self.project)
            print("[%s] connection closing and removing project (non-persistent)" % self.address[0])
        else:
            print("[%s] connection closing (project persisting)" % self.address[0])

    def send_response(self, command, **arguments):
        blob = {
            'cmd': command,
            'data': arguments
        }
        data = "%s\n" % json.dumps(blob)
        self.send(data.encode())


class Project(object):

    def __init__(self, project_name, persists):
        self.project_name = project_name
        self.persists = persists
        self.pages = [Page(self, 'default')]

    def update_persistence(self, persists):
        self.persists = persists

    def get_page(self, page_name, create=True):
        for page in self.pages:
            if page.page_name == page_name:
                return page
        if create:
            new_page = Page(self, page_name)
            self.pages.append(new_page)
            return new_page
        else:
            return None


class Page(object):

    def __init__(self, project, page_name):
        self.project = project
        self.page_name = page_name
        self.sections = []

    def add_section(self, section_name):
        if self.get_section(section_name) is not None:
            return None

        section = Section(self, section_name)
        self.sections.append(section)
        return section

    def get_section(self, section_name):
        for section in self.sections:
            if section.section_name == section_name:
                return section
        return None


class Section(object):

    def __init__(self, page, section_name):
        self.page = page
        self.section_name = section_name
        self.values = []

    def add_value(self, value_name, value_type, value):
        if self.get_value(value_name) is not None:
            return None

        value = Value(self, value_name, value_type, value)
        self.values.append(value)
        return value

    def get_value(self, value_name):
        for value in self.values:
            if value.value_name == value_name:
                return value
        return None


class Value(object):

    def __init__(self, section, value_name, value_type, value):
        self.section = section
        self.value_name = value_name
        self.value_type = value_type
        self.value = value

    def set(self, value):
        self.value = value
