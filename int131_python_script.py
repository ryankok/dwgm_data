import sys
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from urllib.parse import urljoin

def main(user_id):
    # Define the folder path based on user_id
    folder_path = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int131_files/1_input'
    
    url = "https://vicgas.prod.marketnet.net.au/Public_Dir/Archive"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        int131_files = []

        for link in links:
            file_url = link['href']
            if 'int131' in file_url and file_url.endswith('.csv'):
                file_name = os.path.basename(file_url)
                file_download_url = urljoin(url, file_url)
                int131_files.append(file_download_url)

        for csv_url in int131_files:
            file_name = os.path.basename(csv_url)
            file_path = os.path.join(folder_path, file_name)

            if not os.path.exists(file_path):
                response = requests.get(csv_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    print(f'Downloaded: {file_path}')
                else:
                    print(f'Failed to download: {csv_url}')
            #else:
                #print(f'Skipped download - File already exists: {file_path}')
    else:
        print(f'Failed to access the URL: {url}')

    # Paths to the directory and output files
    directory = folder_path
    output_file = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int131_files/2_output/int131_rawdata.csv'

    # List the CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # List to store the loaded data
    data = []

    for csv_file in csv_files:
        csv_file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(csv_file_path)
        
        # Remove rows where 'schedule_type' is 'D + 1 or 'D + 2'
        df = df.loc[~df['schedule_type'].isin(['D + 1', 'D + 2']), :]

        # Add the DataFrame to the list
        data.append(df)

    # Concatenate all DataFrames
    df = pd.concat(data, ignore_index=True)

    # Drop the 'current_date' column, temporarily for deduplication
    df_temp = df.drop('current_date', axis=1)

    # Drop duplicate rows disregarding 'current_date'
    df = df.loc[df_temp.drop_duplicates().index]

    # Save the resulting DataFrame to CSV
    df.to_csv(output_file, index=False)

    print('Combined CSV file created.')

    # Load the data from the CSV file
    file_path2 = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int131_files/2_output/int131_rawdata.csv'
    df = pd.read_csv(file_path2)

    # Replace empty cells with NaN
    df.replace('', pd.NA, inplace=True)

    # Create a copy of the original DataFrame
    df_original = df.copy()

    # Convert step1 to step10 columns to numeric format
    step_columns = df.columns[8:18]  
    df[step_columns] = df[step_columns].apply(pd.to_numeric, errors='coerce')

    # Create a new DataFrame to store intermediate results
    df_intermediate = df.copy()

    # Update the data to represent the increase from the previous step for rows where "type_2" is "c" in the intermediate DataFrame
    for i in range(1, len(step_columns)):
        current_step = step_columns[i]
        previous_step = step_columns[i-1]

        df_intermediate.loc[df['type_2'] == 'c', current_step] = df.loc[df['type_2'] == 'c', current_step] - df.loc[df['type_2'] == 'c', previous_step]

    # Create new columns "step1_ori" to "step10_ori" by copying data from original step1 to step10 columns
    for i, step_col in enumerate(step_columns):
        new_col_name = f"{step_col}_ori"
        df_intermediate[new_col_name] = df_original[step_col]

    column_names = df_intermediate.columns.tolist()

    # Move columns 9 to 19 to the end of the DataFrame
    columns_to_move = column_names[8:18]
    new_column_order = [col for col in column_names if col not in columns_to_move] + columns_to_move
    df_intermediate = df_intermediate[new_column_order]

    # Now, the columns 9 to 19 should be at the end of the DataFrame

    # Assuming df is the DataFrame with step1 to step10 columns at the last 10 columns

    step_columns = df_intermediate.columns[-10:]  # Assuming the last 10 columns are step1 to step10

    # Unpivot the step1 to step10 columns into rows with a new column "bid_steps"
    df_unpivoted = df_intermediate.melt(id_vars=df_intermediate.columns[:-10], value_vars=step_columns, var_name='bid_steps', value_name='value')

    # Sort the dataframe by the original index if needed

    # Assuming df_unpivoted is your original DataFrame

    # Pivot the DataFrame
    df_pivoted = df_unpivoted.pivot_table(index=['gas_date', 'type_1', 'participant_id', 'participant_name', 'code', 'name', 'offer_type','bid_id', 'bid_cutoff_time', 'schedule_type', 'schedule_time', 'current_date','bid_steps'], columns='type_2', values='value', aggfunc='first').reset_index()
    df_pivoted.columns.name = None  # Remove 'type_2' from the column name

    # Rename columns as per desired output
    df_desired = df_pivoted.rename(columns={'a': 'Price', 'c': 'Volume'})

    # Add an additional column to tie the data together
    df_desired['date_time_identifier'] = df_desired['gas_date'].astype(str) + ' ' + df_desired['schedule_time'].astype(str)

    # Export the pivoted data to a new CSV file
    pivoted_file_path = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int131_files/2_output/dwgm_final_raw_data.csv'
    df_desired.to_csv(pivoted_file_path, index=False)

    #print("Data pivoted based on 'type_2' with 'a' and 'c' values as separate columns has been exported to 'dwgm_final_raw_data.csv'.")

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print("Please provide the user ID as a command-line argument.")
