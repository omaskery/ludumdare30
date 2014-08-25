from ld30.dbgsrv.server import dbg_server, http_server

__author__ = 'Oliver Maskery'

import asyncore


def host(debug_target, web_target):
    debug_server = dbg_server.Server(debug_target)
    web_server = http_server.SimpleHttpServer(web_target, debug_server)
    web_server.start()
    asyncore.loop()
