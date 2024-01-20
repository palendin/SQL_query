import pandas as pd
import os, sys
import shutil
import gspread as gs
from tools_and_functions.insert_instrument_to_pgdb import insert_cellcount_csv_to_pg

# define the path to be base path of the PC + the folder containing the data source
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# process -> append to g-sheet -> upload to postgresql
def cell_count_processing(root_directory, archive_directory):
    print(root_directory)
    # Loop through file in directory 

    df_list = []
    fileList = [files for files in os.listdir(root_directory) if files.endswith('.csv')]

    for files in fileList:

    # for files in os.listdir(root_directory):
    #     # for each files + folder in the listdir, get the extension
    #     ext = os.path.splitext(files)[-1].lower()

    #     # process only csv files
    #     if ext == ".csv":
        file_path = os.path.join(root_directory, files)

        try:
            df = pd.read_csv(file_path)
            df = df.iloc[:,0].str.split(':\t', expand=True)
            df = df.set_index(0).transpose()
            df_list.append(df)

            # move files to archive folder after appending to list
            shutil.move(file_path, archive_directory)
        except:
            print('cannot read file or already exist in the archive. If duplicate file, it will still get appended to the csv file')
            continue
        

    # drops the column and reset with another index, renamed to 'id'
    # combined_df = pd.concat(df_list)[df.columns].reset_index(drop=True).rename_axis('id')
    if len(df_list) > 0:
        combined_df = pd.concat(df_list)[df.columns].reset_index().iloc[:,2:] # skip the index and UTC time column
        
        #append to existing csv file, except the header (for troubleshooting purposes)
        #combined_df.to_csv("/Users/wayne/Documents/Programming/vscode/API/SQL_query/nucleocounter_raw_csv/compiled_cell_count/cell_count.csv", mode='a', header=False, index=False)
        
        # export by append to google spreadsheet
        exportDF(combined_df)

        # note that postgresql has serial id, which will auto_index. do not need to worry about having the id column.
        cell_count = "cell_count"
        insert_cellcount_csv_to_pg(combined_df,cell_count)
    else:
        print('no new files to upload')

# using gspread to append to the existing spreadsheet in google doc
def exportDF(df):

    # get service account
    SQL_folder = os.path.dirname(os.path.join(os.path.dirname(os.getcwd()))) #1 lv up (should give you SQL_query path)
    service_account = os.path.join(SQL_folder,'API/Google_API/service_account.json')
    gc = gs.service_account(filename=service_account)


    # open the file that you want data to append to
    sh = gc.open_by_key('1CFYh78GX4T_xjn-nOZT0ysmWQdJCYz7yh3cy97OOe1g') # ('1ruMwYvR5RMSNG1I0EkmASiGAtgSx7Xjr3a_ModEVd2s')

    worksheet = sh.worksheet("cell_counter") # assign sheet
    
    # append to worksheet
    worksheet.append_rows(df.values.tolist())




if __name__ == "__main__":
    # choose path of the cell count folder and archive folder
    process_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Instrument/nucleocounter raw files'
    archive_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Instrument/nucleocounter raw files/Archive (Data Uploaded)'
    #process_folder_path = resource_path('nucleocounter_raw_csv')
    #archive_folder_path = resource_path('nucleocounter_raw_csv/archive')
    cell_count_processing(process_folder_path, archive_folder_path)

