from fastapi import UploadFile
from pathlib import Path
from PIL import Image
import io

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "storage"


def save_upload_file(upload_file: UploadFile, quality: int = 20) -> str:
    file_location = IMAGE_DIR / upload_file.filename

    # Read the uploaded file into a PIL Image
    image = Image.open(upload_file.file)

    # Convert the image to JPEG format for better compression
    if image.format != 'JPEG':
        image = image.convert('RGB')

    # Get the original size
    original_size = upload_file.file.seek(0, io.SEEK_END)
    upload_file.file.seek(0)

    # Compress the image
    with io.BytesIO() as buffer:
        image.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        compressed_size = buffer.getbuffer().nbytes

        with open(file_location, "wb") as out_file:
            out_file.write(buffer.read())

    # Print sizes for verification
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")

    return upload_file.filename
