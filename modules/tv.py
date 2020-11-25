from functools import wraps
from requests.exceptions import ConnectionError, ConnectTimeout
from fastapi import APIRouter, Request
from roku import Roku
from modules.system import token_required, write_log
from modules.devices import get_devices_by_type

tvs = get_devices_by_type("TV")
if len(tvs) > 0:
    data = {"roku": Roku(tvs[0])}  # TODO: temporary until IP mapping is set up.
else:
    data = {"roku": None}
    write_log("tv: TV not set.")

router = APIRouter()

def tv_set(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if data['roku'] is not None:
            func(args, kwargs)
        else:
            return {"message": "TV not set."}
    return inner

@router.get("/tv", tags=['tv'])
@token_required
@tv_set
def tv_status(request: Request, token = None):
    write_log("Triggered /tv")
    return data['roku'].power_state

@router.get("/tv/apps", tags=['tv'])
@token_required
@tv_set
def tv_apps(request: Request, token = None):
    write_log("Triggered /tv/apps")
    apps = []
    for app in data['roku'].apps:
        apps.append(app.name)
    return {"apps": apps}

@router.get("/tv/on", tags=['tv'])
@token_required
@tv_set
def tv_on(request: Request, token = None):
    write_log("Triggered /tv/on")
    try:
        data['roku'].poweron()
        return {"message": "TV On"}
    except (ConnectionError, ConnectTimeout) as e:
        write_log(e)
        return e

@router.get("/tv/off", tags=['tv'])
@token_required
@tv_set
def tv_off(request: Request, token = None):
    write_log("Triggered /tv/off")
    try:
        data['roku'].poweroff()
    except (ConnectionError, ConnectTimeout) as e:
        write_log(e.message)
        return e

@router.get("/tv/vol/{state}", tags=['tv'])
@token_required
@tv_set
def tv_vol(state: str, request: Request, token = None):
    write_log(f"Triggered /tv/vol/{state}")
    if state == "up":
        data['roku'].volume_up()
        return {"message": "Volume up!"}
    if state == "down":
        data['roku'].volume_down()
        return {"message": "Volume down!"}
    if state == "mute":
        data['roku'].volume_mute()
        return {"message": "Volume mute!"}

@router.get('/tv/commands', tags=['tv'])
@token_required
@tv_set
def tv_commands(request: Request, token = None):
    write_log("Triggered /tv/commands")
    return data['roku'].commands

@router.get('/tv/home', tags=['tv'])
@token_required
@tv_set
def tv_home(request: Request, token = None):
    write_log("Triggered /tv/home")
    data['roku'].home()
    return {'message': "home"}

@router.get('/tv/input/{tv_input}', tags=['tv'])
@token_required
@tv_set
def tv_input(tv_input, request: Request, token = None):
    write_log(f"Triggered /tv/input/{tv_input}")
    if tv_input == "hdmi1":
        data['roku'].input_hdmi1()
        return {"message": "Input hdmi1!"}
    if tv_input == "hdmi2":
        data['roku'].input_hdmi2()
        return {"message": "Input hdmi2!"}
    if tv_input == "hdmi3":
        data['roku'].input_hdmi3()
        return {"message": "Input hdmi3!"}

@router.get("/tvs", tags=['tv'])
@token_required
def tv_list(request: Request, token = None):
    return get_devices_by_type("TV")

@router.get("/tvs/{tv_id}")
@token_required
def set_tv(tv_id: int, request: Request, token = None):
    data['roku'] = Roku(get_devices_by_type("TV")[tv_id])
    return {"message": f"TV set to {get_devices_by_type('TV')[tv_id]}"}