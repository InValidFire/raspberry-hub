import uuid
import logging
from peewee import AutoField, ForeignKeyField, Model, IntegerField, TextField, SqliteDatabase, DoesNotExist, DateTimeField, UUIDField, IntegrityError
from playhouse.shortcuts import model_to_dict
from datetime import datetime

db = SqliteDatabase("data.db", pragmas={'foreign_keys': 1})
logger = logging.getLogger(__name__)

def iter_table(model_dict):
    for key in data:
        if not db.table_exists(key):
            db.create_tables([data[key]])
            logger.debug(f"Created table '{key}'")

class BaseModel(Model):
    class Meta:
        database = db

class Device(BaseModel):
    device_uuid = UUIDField(unique=True, primary_key=True, default=uuid.uuid4())
    address = TextField(unique=True)
    kind = TextField()

class Medicine(BaseModel):
    medication_id = AutoField()
    medication = TextField(unique=True)
    dosage = IntegerField()

class MedicineRecord(BaseModel):
    record_id = AutoField()
    medication = ForeignKeyField(Medicine, field="medication_id", )
    datetime_taken = DateTimeField(default=datetime.now)

class APIKey(BaseModel):
    service = TextField(unique=True, primary_key=True)
    key = TextField(unique=True)

class Token(BaseModel):
    token = TextField(unique=True, primary_key=True, default=uuid.uuid4())
    device = ForeignKeyField(Device, field="device_uuid")
    last_used = DateTimeField(default=datetime.now)
    last_ip = TextField()

data = {"medicinerecord": MedicineRecord,
        "device": Device,
        "apikey": APIKey,
        "medicine": Medicine,
        "token": Token}

iter_table(data)