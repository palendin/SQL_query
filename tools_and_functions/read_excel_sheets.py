import pandas as pd

try:
# # Print the file names in the current subfolder
# for file_name in os.listdir(folder_path):
#     print(f" - {file_name}")
    sample_layout = pd.read_excel(folder_path+'/' + 'sample_layout.xlsx',engine='openpyxl',sheet_name=None, skiprows=0) #skip the first row which is the indexes of the well
    measurements = pd.read_excel(folder_path+'/' + 'abs_reading.xlsx',engine='openpyxl',sheet_name=None, skiprows=0) #skip the first row which is the indexes of the well

except:
    raise Exception('cannot read files in folder ')