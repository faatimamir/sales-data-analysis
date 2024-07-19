
import pandas as pd

def load_data(file_path):
    try:
        if file_path.endswith('.xlsx'):
            print("loading...")
            xls = pd.ExcelFile(file_path)
            data = {
                'building_table': pd.read_excel(xls, sheet_name='building_table'),
                'unit_table': pd.read_excel(xls, sheet_name='unit_table'),
                'history_table': pd.read_excel(xls, sheet_name='history_table')
            }
            print("data loaded")
        else:
            raise ValueError("Unsupported file format. Please provide an XLSX file.")
        return data
    except Exception as e:
        raise ValueError(f"Error loading data from file: {str(e)}")

