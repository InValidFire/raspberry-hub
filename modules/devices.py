import uuid
import logging
from modules.system import token_required
from pathlib import Path
from fastapi import APIRouter, Request
import common.database as database
from common.network import get_address
from common.constants import RECORD_NOT_FOUND, POST_SUCCESS

logger = logging.getLogger(__name__)

router = APIRouter()

@router.on_event("startup")
def startup():
    uuid_file = Path("uuid")
    uuid_file.touch(exist_ok=True)
    device_uuid = uuid_file.read_text()
    if device_uuid == "":
        uuid_file.write_text(f"{uuid.uuid4()}")
        device_uuid = uuid_file.read_text()
    device_uuid = uuid.UUID(device_uuid)
    try:
        database.db.connect(reuse_if_open=True)
        device = database.Device.select().where(database.Device.device_uuid == str(device_uuid)).get()
        device.address = get_address()
        logger.info(f"Updated record for device in local database. IP: {device.address}")
    except database.DoesNotExist:
        device = database.Device.create(device_uuid=device_uuid, address=get_address(), kind="hub")
        logger.info(f"Added record for device in local database. IP: {device.address}")
    finally:
        database.db.close()

@router.get("/devices")
@token_required
async def get_device(request: Request, token: str, uuid: str):
    try:
        device = database.Device.select().where(database.Device.device_uuid == uuid).get()
        return device.ip
    except database.DoesNotExist:
        return RECORD_NOT_FOUND
    finally:
        database.db.close()

@router.post("/device")
@token_required
async def post_device(request: Request, token: str, id: str, ip: str, kind: str):
    database.Device(id=id, ip=ip, kind=kind)
    database.db.close()
    return POST_SUCCESS