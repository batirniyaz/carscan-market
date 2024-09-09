from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.utils.excel_file_utils import create_excel_file
import json

router = APIRouter()


@router.get("/export-data")
async def export_data(data, file_name):
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        return {"message": "Invalid data format"}

    file_data = create_excel_file(data_dict, file_name)
    return {"message": "Exporting data", "file": FileResponse(file_data)}
