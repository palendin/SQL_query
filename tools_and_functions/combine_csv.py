import pandas as pd
import os, sys
import glob
import shutil

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

def combine_csv_files(folder_path):

    # df_list = []
    # for files in os.listdir(folder_path):
    #     file_path = os.path.join(folder_path,files)
    #     df = pd.read_csv(file_path)
    #     df_list.append(df)

    # combined_data = pd.concat(df_list, axis= 0, ignore_index=True)

    # print(combined_data)

    #this method is a lot faster without involving pandas to read CSV files and creating CSV in memory
    allFiles = glob.glob(folder_path + "/*.csv")
    #allFiles.sort() # glob lacks reliable ordering, so impose your own if output order matters
    with open(f'{folder_path}/combined.csv', 'wb') as outfile:
        for i, fname in enumerate(allFiles):
            with open(fname, 'rb+') as infile:
                if i != 0:
                    infile.readline()  # Throw away header on all but first file
                # Block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(fname + " has been imported.")
    

if __name__ == "__main__":
    folder = '/Users/wayne/Documents/Programming/vscode/API/SQL_query/Flex2'
    combine_csv_files(folder_path=folder)
