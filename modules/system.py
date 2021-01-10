# pylint: disable=no-name-in-module
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Request
from functools import wraps
from common.constants import EVENT_SCHEDULED, POST_SUCCESS
from pydantic import BaseModel
from common import database, network
from datetime import datetime
import common.scheduler as scheduler
import shlex, subprocess

from starlette.exceptions import HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

class APIKey(BaseModel):
    service: str
    key: str

def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.debug("running token check")
        try:
            token = database.Token.select().where(database.Token.token == kwargs['token']).get()
            token.last_ip = kwargs['request'].client.host
            token.last_used = datetime.now()
            token.save()
            return func(*args, **kwargs)
        except database.DoesNotExist:
            raise HTTPException
        finally:
            database.db.close()
    return inner

@router.on_event("startup")
def master_token():
    try:
        token = database.Token.select().where(database.Token.device == Path("uuid").read_text()).get()
    except database.DoesNotExist:
        token = database.Token.create(token=uuid.uuid4(), device=Path("uuid").read_text(), last_ip=network.get_address())
    finally:
        token.save()
        database.db.close()
        logger.info(f"Master Token: {token.token}")

@router.get("/token")
@token_required
def generate_token(request: Request, token: str, device_uuid: str):
    device = database.Device.select().where(database.Device.device_uuid == device_uuid).get()
    token = database.Token.create(token=uuid.uuid4(), device=device.device_uuid, last_ip=request.client.host)
    token.save()
    database.db.close()
    logger.info(f"Token generated for IP: {token.last_ip} - {token.token}")
    return database.model_to_dict(token)

def restart():
    subprocess.run(shlex.split("shutdown -r now"))

@router.get("/status")
@token_required
def status(request: Request, token: str):
    return "OK"

@router.get("/restart")
@token_required
async def restart_hub(request: Request, token: str):
    scheduler.schedule_event(restart, 3, 1)
    scheduler.run_scheduler()
    return EVENT_SCHEDULED

@router.post("/key")
@token_required
async def key(request: Request, token: str, key: APIKey):
    api_key = database.APIKey.create(service=key.service, key=key.key)
    api_key.save()
    database.db.close()
    return POST_SUCCESS