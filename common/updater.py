from collections import defaultdict
from pathlib import Path
from json import loads
from os import environ
import ghau

update_data = loads(Path("ghau.json").read_text())
update_data = defaultdict(None, update_data)

def build_reboot(reboot: dict):
    command = None
    if reboot['mode'] == 'python':
        command = ghau.python(reboot['file'])
    if reboot['mode'] == 'cmd':
        command = ghau.cmd(reboot['cmd'])
    return command

def get_auth(auth: dict):
    if "env" in auth['key']:
        return environ[auth['key']['env']]
    else:
        return auth['key']

reboot = build_reboot(update_data['reboot'])
# auth = get_auth(update_data['auth'])

updater = ghau.Update(update_data['version'], update_data['repo'], pre_releases=update_data['pre-releases'], reboot=reboot, download=update_data['download'])

def get_update_status():
    return updater.update_check()

def do_update():
    updater.update()

print(get_update_status())