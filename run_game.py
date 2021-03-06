#!/usr/bin/env python3

__author__ = 'Oliver Maskery'

from ld30.dbgsrv.client import Client as DebugClient
from ld30.game import Game as GameClient
import uuid
import json


def main():
    debug_target = 'omaskery.co.uk'

    release = False

    project_name = 'ld30-game'
    project_persists = True

    try:
        settings = json.loads(open('data/settings.json', 'r').read())
    except IOError:
        settings = {}

    if 'uuid' not in settings.keys():
        settings['uuid'] = str(uuid.uuid4())
    system_uuid = settings['uuid']

    if release:
        project_name += ":" + system_uuid
        project_persists = False

    dc = DebugClient(project_name, persist=project_persists)
    dc.connect((debug_target, 45000))

    gc = GameClient(dc, settings)
    gc.run()

    open('data/settings.json', 'w').write(json.dumps(settings))


if __name__ == "__main__":
    main()
