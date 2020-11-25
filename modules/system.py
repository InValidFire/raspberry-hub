from fastapi import APIRouter, Request
from pathlib import Path
from functools import wraps
from ivf import config
import uuid
import datetime
import requests
import socket
import os

from starlette.exceptions import HTTPException

config_file = Path("data/system.json")
token_file = Path("data/token.json")

router = APIRouter()

def generate_file(path: Path, content):
    if not Path('data').exists():
        Path('data').mkdir()
    path.touch()
    if path.read_text() == "":
        path.write_text(content)

generate_file(config_file, "{}")
generate_file(token_file, "{}")

def load_data():
    return config.load(config_file)

def load_token():
    return config.load(token_file)

def get_key():
    data = load_data()
    return data['key']

def generate_token():
    return uuid.UUID(bytes=os.urandom(16), version=4)

def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        print("running token check")
        data = load_token()
        if load_token()['token'] == kwargs['token']:
            data['lastUsed'] = datetime.datetime.now().strftime("%m-%d-%Y | %H:%M:%S")
            if kwargs['request'].client.host not in data['ips']:
                data['ips'].append(kwargs['request'].client.host)
            config.save(token_file, data)
            return func(*args, **kwargs)
        else:
            raise HTTPException(404)
    return inner

def write_log(msg):
    """Write a message to the logs."""
    now = datetime.datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S | ")
    logdir = Path("logs")
    if not logdir.exists():
        logdir.mkdir()
    logfile = Path(f"logs/{date}")
    logfile.touch()  # ensures file exist
    with logfile.open("a+") as f:
        f.write(time+msg+"\n")

def get_site():
    data = load_data()
    return data['site']

def set_site(site: str):
    data = load_data()
    data['site'] = site
    config.save()

def _update_handler(args):
    """Used in the update process to output messages to logs."""
    old_version, new_version = args
    write_log(f"Updated from {old_version} to {new_version}.")

@router.get("/system", tags=['system'])
@token_required
def system_home(request: Request, token = None):
    write_log("Triggered /system")
    return {"module": "active!"}

@router.get("/system/address", tags=['system'])
@token_required
def get_address(request: Request, token = None):
    """Returns the internal and external IP addresses"""
    write_log("Triggered /system/address")
    external = requests.get("https://ipinfo.io/ip").text.rstrip()
    internal = socket.gethostbyname(socket.gethostname())
    return {"internal": internal, "external": external}

@router.get("/system/log", tags=['system'])
@token_required
def get_logs(request: Request, token = None):
    """Returns latest logfile's contents."""
    write_log("Triggered /system/log")
    now = datetime.datetime.now()
    date = now.strftime("%d-%m-%Y")
    logfile = Path(f"logs/{date}")
    return logfile.read_text()

@router.post("/system/shutdown", tags=['system'])  # TODO: schedule instead of immediate
@token_required
def shutdown(request: Request, token = None):
    """Shutdown the system."""
    write_log("Triggered /system/shutdown")
    os.execv("shutdown now")

@router.post("/system/restart", tags=['system'])  # TODO: schedule instead of immediate
@token_required
def reboot(request: Request, token = None):
    """Restart the system."""
    write_log("Triggered /system/restart")
    os.execv("shutdown -r now")

if len(load_data().keys()) == 0:
    print("No system.json file found. Entering API setup.")
    system = {}
    system['site'] = input("Enter API website: ")
    config.save(config_file, system)
    token = {"token": generate_token().hex}
    config.save(token_file, token)
    print(f"Record this somewhere, it won't be displayed again:\ntoken: {token['token']}")