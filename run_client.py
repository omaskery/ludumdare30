#!/usr/bin/env python3

__author__ = 'Oliver Maskery'

from dbgsrv.client import Client as DebugClient
from client import Client as GameClient
import uuid
import json


def main():
    target = 'teamfrag.net'

    release = False

    project_name = 'ld30-client'
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

    gc = GameClient(target, dc, settings)
    gc.run()

    open('settings.json', 'w').write(json.dumps(settings))


if __name__ == "__main__":
    main()
