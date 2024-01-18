import psycopg2
from psycopg2 import Error
import json
import os

# table_name = 'cell_count' 
# column_map = os.path.join(os.path.dirname(os.getcwd()),f'column_map/{table_name}.json')
# print(column_map)

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
    
        # mapping for cell count
        column_map = os.path.join(os.getcwd(),f'column_map/{table_name}.json') # brings back to SQL_query path, and then go to json file in column_map folder
        with open(column_map, 'r') as file:
            map = json.load(file)

        # if table_name == "cell_count":
        #     column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/cell_count.json"
        #     # json file maps csv column names to postgresql column names
        #     with open(column_map, 'r') as file:
        #         map = json.load(file)

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

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")


def insert_flex_csv_to_pg(combined_df, table_name):
    df = combined_df
    df_length = len(df)

    try:
        connection = psycopg2.connect(
        host="34.134.210.165",
        database="vitrolabs",
        user="postgres",
        password="Vitrolabs2023!",
        port=5432)
        
        cur = connection.cursor()
    
        # mapping for flex
        column_map = os.path.join(os.getcwd(),f'column_map/{table_name}.json')
        print(column_map)
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

        # query to get the length of the table
        table_length_query = f"SELECT COUNT(*) FROM instrument.{table_name}"
        cur.execute(table_length_query)
        # Fetch the table length result
        row_count = cur.fetchone()[0]
        
        # get the differential dataframe
        if row_count < df_length:
            print(row_count)
            df = df.iloc[row_count:df_length,:]
    
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

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")