#!/usr/bin/env python3

__author__ = "pyd4nt1c"
__version__ = 1.0


# -- Imports --
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
import os.path
from requests import post
import mimetypes
import time
import json
# -------------


app = FastAPI(
    title="File downloading API",
    description="Backend API for downloading files, with captcha protection"
)

# Templates directory
templates = Jinja2Templates(directory="templates")

app.mount(
    "/static", StaticFiles(directory="static"), name="static")

# -- Constants --
BASE_URL = "https://p4wn.eu/"

SITE_KEY = "6Lezv-MZAAAAAHTFigO2zL-lJPgejkyDYDM-I_dt"
SECRET_KEY = "****************************************"

# Defined units
UNITS_MAPPING = [
    (1 << 50, ' PB'),
    (1 << 40, ' TB'),
    (1 << 30, ' GB'),
    (1 << 20, ' MB'),
    (1 << 10, ' KB'),
    (1, (' byte', ' bytes')),
]
# --------------


# -- Functions --
def verify_captcha(captcha_token):
    "Verify reCAPTCHA token using Google's API"
    url = "https://www.google.com/recaptcha/api/siteverify"
    parameters = {
        "secret": SECRET_KEY,
        "response": captcha_token
    }
    response = post(url, data=parameters)
    response = json.loads(str(response.text))

    if response.get("success") == True:
        return True
    else:
        return False


def convertsize(bytes, units=UNITS_MAPPING):
    "Convert size from bytes to human readable format"
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


def get_icon(file_type):
    "Return Font Awesome icon class based on file type"
    if file_type == "Unknown":
        return "fas fa-file"
    file_type = file_type[0]
    full_file_type = file_type
    file_type = file_type.split("/")
    file_type = file_type[1]
    if file_type == "javascript":
        icon = "fab fa-js"
    elif file_type == "msword":
        icon = "fas fa-file-word"
    elif file_type == "javascript":
        icon = "fab fa-js"
    elif file_type == "pdf":
        icon = "fas fa-file-pdf"
    elif file_type == "vnd.ms-excel":
        icon = "fas fa-file-excel"
    elif file_type == "vnd.ms-powerpoint":
        icon = "fas fa-file-powerpoint"
    elif file_type == "vnd.ms-excel":
        icon = "fas fa-file-excel"
    elif file_type == {"x-tar", "zip"}:
        icon = "fas fa-archive"
    elif file_type in {"mp4", "x-msvideo", "quicktime"} or full_file_type == "video/mpeg":
        icon = "fas fa-video"
    elif file_type == "css":
        icon = "fab fa-css3"
    elif file_type == "html":
        icon = "fab fa-html5"
    elif file_type == "x-python":
        icon = "fab fa-python"
    elif file_type in {"plain", "json"}:
        icon = "fas fa-file-alt"
    elif file_type in {"xml", "x-sh"}:
        icon = "fas fa-code"
    elif file_type in {"jpeg", "gif", "bmp", "png", "svg+xml"}:
        icon = "fas fa-image"
    elif file_type == "x-wav" or full_file_type in {"audio/mpeg", "audio/basic"}:
        icon = "fas fa-volume-up"
    else:
        icon = "fas fa-file"
    return icon


def get_size(file):
    "Get file size"
    try:
        file_size = os.path.getsize("files/" + file)
        file_size = convertsize(file_size)
        return file_size
    except:
        file_size = "Unknown"
        return file_size


def get_type(file):
    "Get MIME type of a file based on it's extension"
    file_type = mimetypes.guess_type("files" + file, strict=True)
    if file_type is None:
        return "Unknown"
    else:
        return file_type


def get_creation_date(file):
    "Get the date of creation of a file"
    try:
        creation_date = time.ctime(os.path.getctime("files/" + file))
        return creation_date
    except:
        return "Unknown"
# ---------------


# -- Paths --
@app.get("/")
def get_root():
    return PlainTextResponse("No")


@app.get("/favicon.ico")
def get_favicon():
    return FileResponse("favicon.ico")


@app.get("/{file}")
def file_details(request: Request, file: str):
    # Check if the file exists
    if not os.path.isfile("files/" + file):
        raise HTTPException(status_code=404, detail="File not found")

    file_type = get_type(file)
    icon = get_icon(file_type)
    file_encoding = mimetypes.guess_type("files/" + file)[1]
    if file_encoding is None:
        file_encoding = "None"
    if file_type != "Unknown":
        file_type = file_type[0]
    file_size = get_size(file)
    creation_date = get_creation_date(file)

    return templates.TemplateResponse("file_details.html", {
        "request": request,
        "BASE_URL": BASE_URL,
        "SITE_KEY": SITE_KEY,
        "icon": icon,
        "file_name": file,
        "file_type": file_type,
        "file_encoding": file_encoding,
        "file_size": file_size,
        "creation_date": creation_date
    })


@app.get("/download/{file}")
def download_file(file: str, captcha_token: str):
    if len(file) > 100:  # Check if the file name isn't too long
        raise HTTPException(status_code=400, detail="File name too long")
    # Check if the file exists
    if not os.path.isfile("files/" + file):
        raise HTTPException(status_code=404, detail="File not found")

    # Verify captcha
    if not verify_captcha(captcha_token):
        raise HTTPException(status_code=403, detail="Captcha token invalid")

    # If everything matches up
    return FileResponse("files/" + file)


@app.get("/edit/{file}")
def view_file(file: str):
    if len(file) > 100:  # Check if the file name isn't too long
        raise HTTPException(status_code=400, detail="File name too long")

# -----------
