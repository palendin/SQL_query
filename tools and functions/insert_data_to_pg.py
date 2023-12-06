import psycopg2
from psycopg2 import Error
import pandas as pd
import numpy as np

# read data from file
data = pd.read_csv('/Users/wayne/Documents/Programming/vscode/API/SQL_query/Master_HP_assay/HP_assay_master_data.csv', na_values=['NaN'])
#data = pd.read_csv('experiment_detail.csv')

# Replace NaN values with None
df = data.where(pd.notna(data), None)


# Define the table name
table_name = 'hp_assay'

try:
    connection = psycopg2.connect(
        host="localhost",
        database="sample_database",
        user="postgres",
        password="Vitrolabs2023",
        port=5432)

    cur = connection.cursor()

# Define the CSV file path
    #csv_file_path = '/Users/wayne/Documents/Programming/vscode/API/SQL_query/experiment_detail.csv'
    
    # Check if the table exists
    query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
    cur.execute(query, (table_name,))
    table_exists = cur.fetchone()[0]

    if table_exists:
        print(f"The table '{table_name}' exists.")
    else:
        print(f"The table '{table_name}' does not exist.")
        raise Exception('create table in postgresql first')

    # Generate the column names dynamically
    columns = ', '.join(df.columns)

    # Generate the placeholders for the VALUES clause based on the number of columns
    placeholders = ', '.join(['%s'] * len(df.columns))

    # Create the INSERT query
    query = f'''INSERT INTO pizza_schema.{table_name}({columns}) VALUES ({placeholders})''' # ON CONFLICT (id) DO NOTHING'''

    # Insert data from the DataFrame
    # cur.executemany(query, data)
    # connection.commit()
    for _, row in df.iterrows():
        cur.execute(query, tuple(row))
        
    connection.commit()

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cur.close()
        connection.close()
        print("PostgreSQL connection is closed")

