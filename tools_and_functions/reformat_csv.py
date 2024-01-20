import pandas as pd
import os, sys

# reformat csv when csv contains information in only 1 column separated by a character or symbol

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path
    
def processing(root_directory):
    print(root_directory)
    # Loop through file in directory 

    df_list = []
    for files in os.listdir(root_directory):
        file_paths = os.path.join(root_directory, files)

        try:
            df = pd.read_csv(file_paths)
        except:
            print('file not found')
        
        
        df = df.iloc[:,0].str.split(':\t', expand=True)
        df = df.set_index(0).transpose()
        df_list.append(df)
    
    # drops the column and reset with another index, renamed to 'id'
    combined_df = pd.concat(df_list)[df.columns].reset_index(drop=True).rename_axis('id')
    print(combined_df)
    combined_df.to_csv('test.csv')

        

if __name__ == "__main__":
    path = resource_path('nucleocounter_raw_csv')
    processing(path)



