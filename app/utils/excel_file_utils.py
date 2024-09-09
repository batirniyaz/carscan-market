import pandas as pd


def create_excel_file(data, file_name):
    df = pd.DataFrame(data['graphic'])
    df.to_excel(f"{file_name}.xlsx", index=False)
    return f"{file_name}.xlsx"
