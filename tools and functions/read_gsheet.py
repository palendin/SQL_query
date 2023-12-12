import pandas as pd
import gspread as gs

path = "/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data [UNDER CONSTRUCTION, DO NOT USE]/Analytical/Analytical Experiment Tracker.gsheet"

gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')

# open the file that you want data to append to
sh = gc.open_by_key('1MOuCpubEbwf7QE_tU5IfL_pqFwtDukOqH5o_9Z0WnHM')

worksheet = sh.worksheet("Tracker") # assign sheet

# append to worksheet
list_of_lists = worksheet.get_all_values()

df = pd.DataFrame(list_of_lists[1:], columns = list_of_lists[0])

df = df.reset_index(drop=True)

print(df.head())
