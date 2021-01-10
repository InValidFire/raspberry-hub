from fastapi import FastAPI

from modules import system, devices, weather, medicine

app = FastAPI(docs_url=None, redoc_url=None)

app.include_router(devices.router)
app.include_router(system.router)
app.include_router(weather.router)
app.include_router(medicine.router)