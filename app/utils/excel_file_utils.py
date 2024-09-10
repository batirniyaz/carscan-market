import os

import pandas as pd


async def create_excel_file(data, file_name: str):
    df = pd.DataFrame(data)
    reports_dir = "app/reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)

    excel_file_path = os.path.join(reports_dir, f"{file_name}.xlsx")
    df.to_excel(excel_file_path, index=False)
    return excel_file_path
