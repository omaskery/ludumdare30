#!/usr/bin/env python3

__author__ = 'Oliver Maskery'

from dbgsrv.client import Client as DebugClient
from server import Server as GameServer
import uuid
import json


def main():
    target = 'teamfrag.net'

    release = False

    project_name = 'ld30-server'
    project_persists = True

    try:
        settings = json.loads(open('settings.json', 'r').read())
    except IOError:
        settings = {
            'uuid': str(uuid.uuid4())
        }

    system_uuid = settings['uuid']

    if release:
        project_name += ":" + system_uuid
        project_persists = False

    dc = DebugClient(project_name, persist=project_persists)
    dc.connect((target, 45000))

    gc = GameServer(dc, settings)
    gc.run()


if __name__ == "__main__":
    main()
