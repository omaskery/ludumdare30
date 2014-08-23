#!/usr/bin/env python3

__author__ = 'Oliver Maskery'


from ld30.dbgsrv.client import Client as DebugClient
from ld30.server import Server as GameServer
import signal
import uuid
import json


class SigintExitFlag(object):

    def __init__(self):
        self.kill_flag = False
        signal.signal(signal.SIGINT, self.handle_kill_signal)

    def handle_kill_signal(self, *ignore):
        self.kill_flag = True

    def should_exit(self):
        return self.kill_flag


def main(**kwargs):
    debug_target = 'omaskery.co.uk'

    release = False

    project_name = 'ld30-server'
    project_persists = True

    if 'exit_flag' in kwargs.keys():
        exit_flag = kwargs['exit_flag']
    else:
        exit_flag = SigintExitFlag()

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
    dc.connect((debug_target, 45000))

    gc = GameServer(dc, settings, exit_flag)
    gc.run()


if __name__ == "__main__":
    main()
