import pandas as pd
import os, sys
import psycopg2
from psycopg2 import Error
import shutil

# define the path to be base path of the PC + the folder containing the data source
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# since the files have same format and doesnt need to be opened, can move to archive after finishing
def cell_count_processing(root_directory, archive_directory):
    print(root_directory)
    # Loop through file in directory 

    df_list = []
    for files in os.listdir(root_directory):
        
        # for each files + folder in the listdir, get the extension
        ext = os.path.splitext(files)[-1].lower()

        # process only csv files
        if ext == ".csv":
            file_path = os.path.join(root_directory, files)
        # make a text file if not exist
        # txtfile_path = os.path.join(os.path.dirname(__file__), 'cellcount_processed_files.txt')
        # if not os.path.exists(txtfile_path):
        #     with open(txtfile_path, 'w'):
        #         pass
        # else:
        #     pass

        # remembered_folders_file = 'cellcount_processed_files.txt'
        # with open(remembered_folders_file, 'r+') as f:
        #     if file_path not in f.read():   

        #         try:
        #             df = pd.read_csv(file_path)
        #         except:
        #             print('file not found')
            try:
                df = pd.read_csv(file_path)
                df = df.iloc[:,0].str.split(':\t', expand=True)
                df = df.set_index(0).transpose()
                df_list.append(df)

                shutil.move(file_path, archive_directory)
            except:
                print('cannot read file or already exist in the archive. If duplicate file, it will still get appended to the csv file')
                continue
            
    
            #f.write(file_path + ',')  # -------- instead of writing the path to text, can push the file to archive folder  
        
    try:
        # drops the column and reset with another index, renamed to 'id'
        # combined_df = pd.concat(df_list)[df.columns].reset_index(drop=True).rename_axis('id')
        combined_df = pd.concat(df_list)[df.columns].reset_index(drop=True)
        
        # append to existing csv file, except the header
        combined_df.to_csv("/Users/wayne/Documents/Programming/vscode/API/SQL_query/nucleocounter_raw_csv/compiled_cell_count/cell_count.csv", mode='a', header=False, index=False)

        #print(combined_df)
        #combined_df.to_csv('test.csv')
    except:
        print('no new files')



    return combined_df


# need to edit 12/5/2023
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

        # need mapping for cell count
        # if table_name == "biopsy_result":
        # column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/biopsy_map.json"
        # json file maps csv column names to postgresql column names
        # with open(column_map, 'r') as file:
        #     map = json.load(file)


        df = df.fillna(0).replace([0],[None])
        df = df[df['id'].notna()] # get all rows that does not have null id
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
        postgresql_columns = df.columns
        for col in df.columns:
            postgresql_column_name = map.get(col, col)
            postgresql_columns.append(postgresql_column_name)
    
        # Generate the column names dynamically for postgresql query format
        columns = ', '.join(postgresql_columns)
    
        # Generate the placeholders for the VALUES clause based on the number of columns
        placeholders = ', '.join(['%s'] * len(df.columns))

        # Create the INSERT query (will insert even if duplicate, but conflict will dictates what it will do
        query = f'''INSERT INTO biomaterial_scaffold.{table_name}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'''


        data_values = [tuple(row) for _, row in df.iterrows()]
        cur.executemany(query, data_values)
     
        connection.commit()
        print('biomaterial upload success')

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
    process_folder_path = resource_path('nucleocounter_raw_csv')
    archive_folder_path = resource_path('nucleocounter_raw_csv/archive')
    cell_count_processing(process_folder_path, archive_folder_path)
