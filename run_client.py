#!/usr/bin/env python3

__author__ = 'Oliver Maskery'

from ld30.dbgsrv.client import Client as DebugClient
from ld30.client import Client as GameClient
import uuid
import json


def main():
    debug_target = 'omaskery.co.uk'
    target = 'localhost'

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
        target = 'teamfrag.net'

    dc = DebugClient(project_name, persist=project_persists)
    dc.connect((debug_target, 45000))

    gc = GameClient(target, dc, settings)
    gc.run()

    open('settings.json', 'w').write(json.dumps(settings))


if __name__ == "__main__":
    main()
