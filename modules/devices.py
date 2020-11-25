from modules.system import write_log, token_required
from fastapi import APIRouter, Request
from pathlib import Path
from ivf import config
import requests

from pydantic import BaseModel

router = APIRouter()

config_file = Path("data/devices.json")
if not Path("data").exists():
    Path('data').mkdir()
config_file.touch()
if config_file.read_text() == "":
    config_file.write_text("[]")

class Device(BaseModel):
    identifier: int
    address: str
    kind: str

def load_data() -> list:
    return config.load(config_file)

def get_id():
    data = load_data()
    num = 0
    for device in data:
        if data[device]['id'] >= num:
            num = data[device]['id']+1
            print(num)
    return num

def write_data(device: Device, data: list = load_data()):
    device = {"address": device.address, "kind": device.kind, "id": device.identifier}
    for item in data:
        if item['id'] == device['id']:
            data[data.index(item)] = device
            config.save(config_file, data)
            return
    data.append(device)
    config.save(config_file, data)

def get_devices_by_type(type: str):
    data = load_data()
    devices = []
    for device in data:
        if device['kind'] == type:
            devices.append(device['address'])
    return devices

def get_device_by_id(device_id: int):
    data = load_data()
    return data[device_id]

@router.post("/devices", tags=['devices'])
@token_required
def add_device(device: Device, request: Request, token = None):
    write_log(f"Posted to /devices with device: {device.identifier} - {device.address} - {device.kind}")
    write_data(device)
    return load_data()

@router.get("/devices", tags=['devices'])
@token_required
def get_devices(request: Request, token = None):
    write_log(f"Triggered /devices")
    data = load_data()
    return data

def send_to_device(ip: str, route: str):
    r = requests.get(ip+route).text.rstrip()
    return r