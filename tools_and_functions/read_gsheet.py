import pandas as pd
import gspread as gs

def read_gsheet(file_id, sheet_name):

    gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')

    # open the file that you want data to append to
    sh = gc.open_by_key(file_id)

    worksheet = sh.worksheet(sheet_name) # assign sheet

    # append to worksheet
    list_of_lists = worksheet.get_all_values()

    df = pd.DataFrame(list_of_lists[1:], columns = list_of_lists[0]) # [1:] is used cuz not pulling header row

    df = df.reset_index(drop=True)

    return df

def read_gsheet_all_tabs(file_id):

    df_list = []
    gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')

    # open the file that you want data to append to
    sh = gc.open_by_key(file_id)
    
    for worksheet in sh.worksheets():

        # append to worksheet
        list_of_lists = worksheet.get_all_values()

        df = pd.DataFrame(list_of_lists[1:], columns = list_of_lists[0])

        df = df.reset_index(drop=True)
        
        df_list.append(df)
    
    return df_list

if __name__ == "__main__":
    file_id = '1-n2zwPWklDmYvsyYcuaSqdirkg1vnwAaMFXQvvDCyLc'
    sheet_name = "Tracker"
    print(read_gsheet_all_tabs(file_id))

