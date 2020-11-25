from pathlib import Path
import subprocess
from collections import Counter
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ivf import config
import shlex
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules import system, tv, medicine, devices, spotify
from modules.system import generate_file

class EnsureSecurity(StarletteHTTPException):
    pass

ip_blocks = Path("data/blockedips.json")
generate_file(ip_blocks, "[]")

app = FastAPI(docs_url=None, redoc_url=None)

@app.exception_handler(StarletteHTTPException)
def block_ip(request: Request, exc):
    if (request['path'] == "/favicon.ico"):
        return JSONResponse(
        status_code=404,
        content={"message": "no favicon"}
    )
    subprocess.Popen(shlex.split(f"ufw insert 1 deny from {request.client.host} to any"), stdout=subprocess.DEVNULL)
    print(f"Blocking IP {request.client.host}")
    data = config.load(ip_blocks)
    if request.client.host not in data:
        data.append(request.client.host)
        config.save(ip_blocks, data)
    return JSONResponse(
        status_code=404,
        content={"message": "ip blocked"}
    )

def unblock_ip(ip):
    subprocess.Popen(shlex.split(f"ufw delete deny from {ip} to any"), stdout=subprocess.DEVNULL)
    print(f"Unblocking IP {ip}")
    data = config.load(ip_blocks)
    if ip in data:
        data.remove(ip)
        config.save(ip_blocks, data)

app.include_router(system.router)
app.include_router(tv.router)
app.include_router(medicine.router)
app.include_router(devices.router)
app.include_router(spotify.router)