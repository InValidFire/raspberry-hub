# pylint: disable=no-name-in-module

from common.constants import FK_NOT_FOUND, POST_SUCCESS, RECORD_NOT_FOUND
from datetime import datetime
from fastapi import APIRouter
import common.database as database

router = APIRouter()

@router.post("/medicine")
def post_medicine(medication: str, dosage: int):
    mecicine = database.Medicine(medication=medication, dosage=dosage)
    mecicine.save()
    database.db.close()
    return POST_SUCCESS

@router.post("/medicine/record")
def post_medicine_record(medicine):
    try:
        medicine = database.MedicineRecord(medication=medicine)
        medicine.save()
        return POST_SUCCESS
    except database.IntegrityError:
        return FK_NOT_FOUND
    finally:
        database.db.close()

@router.get("/medicine/record")
def get_medicine():
    response = []
    medicine = database.MedicineRecord.select().where(database.MedicineRecord.datetime_taken >= datetime.now().date())
    for record in medicine:
        response.append(database.model_to_dict(record))
    return response