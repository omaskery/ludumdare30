__author__ = 'Oliver Maskery'


import socket
import json


class QueryException(Exception):
    pass


class Client(object):

    def __init__(self, project_name, **kwargs):
        self.project_name = project_name

        if 'persist' in kwargs.keys():
            self.persist = bool(kwargs['persist'])
        else:
            self.persist = False

        self.handle = None
        self.buf = ''

    def connect(self, target):
        self.handle = socket.socket()
        self.handle.connect(target)

        response = self.perform_query('connect', project_name=self.project_name, persist=self.persist)

        return response

    def set_non_blocking(self, timeout=0.5):
        self.handle.set_timeout(timeout)

    def send_blob(self, blob):
        data = "%s\n" % json.dumps(blob)
        self.handle.send(data.encode())

    def read_blob(self):
        while self.buf.find("\n") == -1:
            self.buf += self.handle.recv(2048).decode()

        found = self.buf.find("\n")
        data = self.buf[:found]
        self.buf = self.buf[found+1:]

        return json.loads(data)

    def perform_query(self, command, **arguments):
        blob = {
            'cmd': command,
            'args': arguments
        }

        self.send_blob(blob)
        response = self.read_blob()

        if response['cmd'] != command:
            raise QueryException("expected response to '%s' command, got response to '%s' command" % (
                command, response['cmd']
            ))

        if 'data' not in response.keys():
            raise QueryException("expected a data value in response blob")

        if 'error' in response['data'].keys():
            raise QueryException("error in '%s' query: %s" % (command, response['data']['error']))

        return response

    def try_perform_query(self, command, **arguments):
        try:
            return self.perform_query(command, **arguments), True
        except QueryException as ex:
            return ex, False

    def get_page(self, page_name='default'):
        response = self.perform_query('get-page', page=page_name)

        if not response['data']['success']:
            return None

        page = Page(self, page_name)

        return page

    def list_pages(self):
        response = self.perform_query('list-pages')
        return response['data']['pages']


class Page(object):

    def __init__(self, client, page_name):
        self.client = client
        self.page_name = page_name

    def add_section(self, section_name, ignore_failure=False):
        response, success = self.client.try_perform_query('add-section', page=self.page_name, section=section_name)

        if not success:
            if ignore_failure:
                return None
            else:
                raise response

        if not response['data']['success']:
            return None

        section = Section(self, section_name)

        return section

    def get_section(self, section_name, ignore_failure=False):
        response, success = self.client.try_perform_query('get-section', page=self.page_name, section=section_name)

        if not success:
            if ignore_failure:
                return None
            else:
                raise response

        if not response['data']['success']:
            return None

        section = Section(self, section_name)

        return section

class Section(object):

    def __init__(self, page, section_name):
        self.page = page
        self.section_name = section_name

    def add_value(self, value_name, value_type, value, ignore_failure=False):
        response, success = self.page.client.try_perform_query('add-value',
                                                               page=self.page.page_name,
                                                               section=self.section_name,
                                                               value_name=value_name,
                                                               value_type=value_type,
                                                               value=value)

        if not success:
            if ignore_failure:
                return None
            else:
                raise response

        if not response['data']['success']:
            return None

        value = Value(self, value_name, value_type, value)

        return value

    def get_value(self, value_name, value_type, value, ignore_failure=False):
        response, success = self.page.client.try_perform_query('get-value',
                                                               page=self.page.page_name,
                                                               section=self.section_name,
                                                               value_name=value_name,
                                                               value_type=value_type,
                                                               value=value)

        if not success:
            if ignore_failure:
                return None
            else:
                raise response

        if not response['data']['success']:
            return None

        value = Value(self, value_name, value_type, value)

        return value


class Value(object):

    def __init__(self, section, value_name, value_type, value):
        self.section = section
        self.value_name = value_name
        self.value_type = value_type
        self.value = value

    def set(self, value):
        response = self.section.page.client.perform_query('set-value',
                                                          page=self.section.page.page_name,
                                                          section=self.section.section_name,
                                                          value_name=self.value_name,
                                                          value=value)

        return response['data']['success']
