__author__ = 'Oliver Maskery'

from . import http_server
from . import dbg_server
import asyncore


def host(debug_target, web_target):
    debug_server = dbg_server.Server(debug_target)
    web_server = http_server.SimpleHttpServer(web_target, debug_server)
    web_server.start()
    asyncore.loop()
