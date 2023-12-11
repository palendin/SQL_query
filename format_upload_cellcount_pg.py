import pandas as pd
import os, sys
import psycopg2
from psycopg2 import Error
import shutil
import gspread as gs
import json

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
    combined_df = pd.concat(df_list)[df.columns].reset_index().iloc[:,2:] # skip the index and UTC time column
    
    #append to existing csv file, except the header (for troubleshooting purposes)
    combined_df.to_csv("/Users/wayne/Documents/Programming/vscode/API/SQL_query/nucleocounter_raw_csv/compiled_cell_count/cell_count.csv", mode='a', header=False, index=False)
    
    # export by append to google spreadsheet
    exportDF(combined_df)

    # note that postgresql has serial id, which will auto_index. do not need to worry about having the id column.
    cell_count = "cell_count"
    insert_cellcount_csv_to_pg(combined_df,cell_count)


# using gspread to append to the existing spreadsheet in google doc
def exportDF(df):

    # get service account
    gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')

    # open the file that you want data to append to
    sh = gc.open_by_key('1CFYh78GX4T_xjn-nOZT0ysmWQdJCYz7yh3cy97OOe1g') # ('1ruMwYvR5RMSNG1I0EkmASiGAtgSx7Xjr3a_ModEVd2s')

    worksheet = sh.worksheet("cell_counter") # assign sheet
    
    # append to worksheet
    worksheet.append_rows(df.values.tolist())


def insert_cellcount_csv_to_pg(combined_df, table_name):
    df = combined_df
    try:
        connection = psycopg2.connect(
        host="34.134.210.165",
        database="vitrolabs",
        user="postgres",
        password="Vitrolabs2023!",
        port=5432)
        
        cur = connection.cursor()
    
        # nmapping for cell count
        if table_name == "cell_count":
            column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/cell_count_map.json"
            # json file maps csv column names to postgresql column names
            with open(column_map, 'r') as file:
                map = json.load(file)

        df = df.fillna(0).replace([0],[None])
        df = df[df['Sample ID'].notna()] # get all rows that does not have null sample id

        # Check if the table exists
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        cur.execute(query, (table_name,))
        table_exists = cur.fetchone()[0]

        if table_exists:
            print(f"The table '{table_name}' exists.")
        else:
            print(f"The table '{table_name}' does not exist.")
            raise Exception('create table in postgresql first with desired names. Make sure json names match them')

    
        # column map
        postgresql_columns = []

        for col in df.columns:
            postgresql_column_name = map.get(col, col)
            postgresql_columns.append(postgresql_column_name)

        # Generate the column names dynamically for postgresql query format
        columns = ', '.join(postgresql_columns)

        # Generate the placeholders for the VALUES clause based on the number of columns
        placeholders = ', '.join(['%s'] * len(df.columns))
        # Create the INSERT query (will insert even if duplicate, but conflict will dictates what it will do
        query = f'''INSERT INTO instrument.{table_name}({columns}) VALUES ({placeholders}) ''' #ON CONFLICT (id) DO NOTHING'''

        data_values = [tuple(row) for _, row in df.iterrows()]
        cur.executemany(query, data_values)
    
        connection.commit()
        print('data from {} upload success'.format(table_name))

        # rows_to_upload = 50
        # chunk_size = 10
        # start=0
        # end=0
        # while end <= rows_to_upload:
            
        #     start, end = (start, start+chunk_size)
        #     print(start,end)
        #     start = end
            

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == "__main__":
    # choose path of the cell count folder and archive folder
    process_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data [UNDER CONSTRUCTION, DO NOT USE]/Instrument/nucleocounter raw files'
    archive_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data [UNDER CONSTRUCTION, DO NOT USE]/Instrument/nucleocounter raw files/Archive (Data Uploaded)'
    #process_folder_path = resource_path('nucleocounter_raw_csv')
    #archive_folder_path = resource_path('nucleocounter_raw_csv/archive')
    cell_count_processing(process_folder_path, archive_folder_path)
