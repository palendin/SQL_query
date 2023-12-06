import psycopg2
from psycopg2 import Error
import pandas as pd
import requests
#from opvia_api import OpviaAPI

#api = OpviaAPI(("https://restapi.opvia.io/v0/tables' -H 'Authorization: Bearer {opviaApiKey}"))

try:
    connection = psycopg2.connect(
        host="localhost",
        database="sample_database",
        user="postgres",
        password="Vitrolabs2023",
        port=5432)

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    #print("PostgreSQL server information")
    #print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    #print("You are connected to - ", record, "\n")

    # select data table
    data = '''SELECT * from pizza_schema.experiment_detail'''
    
    #Executing the query
    cursor.execute(data)
    
    #Get column names
    header = [desc[0] for desc in cursor.description]
    
    #Fetching 1st row from the table
    result = cursor.fetchall();
    
    #from SQL to dataframe
    df = pd.DataFrame(result, columns = header)
    print(df)
    #df.to_csv('sample data.csv')

    #upload data to Opvia


except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

