# TODO: send notification to nodes when 12hrs in-between medication
from modules.system import token_required, generate_file
from typing import List
from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from pathlib import Path
from ivf import config

router = APIRouter()
DATE_FORMAT = "%m-%d-%y"

config_file = Path("data/medicine.json")
generate_file(config_file, "{}")

class Record(BaseModel):
    medication: str
    date: str
    time: str

def load_data():
    return config.load(config_file)

def write_data(record: Record, data = load_data()):
    if record.date in data:
        if record.medication in data[record.date]:
            data[record.date][record.medication] += [record.time]
            config.save(config_file, data)
        else:
            data[record.date][record.medication] = []
            write_data(record, data)
    else:
        data[record.date] = {}
        write_data(record, data)

@router.get("/medicine/records/{date}", tags=['medicine'])
@token_required
def get_date(date, request: Request, token = None):
    data = load_data()
    if date in data:
        return data[date]
    else:
        return {"message": "Record not found."}

@router.get("/medicine", tags=['medicine'])
@token_required
def get_today(request: Request, token = None):
    now = datetime.now()
    date = now.strftime(DATE_FORMAT)
    data = load_data()
    if date in data:
        return data[date]
    else:
        return {'message': "No record for today."}

@router.get("/medicine/lastTaken", tags=['medicine'])
@token_required
def get_last_taken(request: Request, token = None, medicine = None):  # TODO: Refactor this
    data = load_data()
    dates: List[datetime] = []
    for date in data:
        dates.append(datetime.strptime(date, DATE_FORMAT))
    latest_date = max(dates).strftime(DATE_FORMAT)
    latest_time = data[latest_date][medicine][-1]
    hours = int(latest_time.split(".")[0])
    minutes = int(latest_time.split(".")[1])
    relative = (datetime.now()-(max(dates)+timedelta(hours=hours, minutes=minutes)))
    return {"date": latest_date, "time": latest_time, "relativeToNow": ":".join(str(relative).split(".")[0].split(":")[:2])}

@router.post("/medicine", tags=['medicine'])
@token_required
def new_record(record: Record, request: Request, token = None):
    write_data(record)
    return load_data()