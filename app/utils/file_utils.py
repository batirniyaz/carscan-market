from fastapi import UploadFile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "storage"


def save_upload_file(upload_file: UploadFile) -> str:
    file_location = IMAGE_DIR / upload_file.filename
    with open(file_location, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return upload_file.filename
