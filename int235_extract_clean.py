import sys
import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime

def main(user_id):
    # Define the folder path based on user_id
    folder_path = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int235_files/1_input'

    url = "https://vicgas.prod.marketnet.net.au/Public_Dir/Archive"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        int235_files = []

        for link in links:
            file_url = link['href']
            if 'int235' in file_url and file_url.endswith('.csv'):  
                file_name = os.path.basename(file_url)
                file_download_url = urljoin(url, file_url)  
                int235_files.append(file_download_url)

        for csv_url in int235_files:
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
    output_file = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int235_files/2_output/int235_rawdata.csv'

    # List the CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # List to store the loaded data
    data = []

    # Iterate through each CSV file and load the data
    for csv_file in csv_files:
        csv_file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(csv_file_path)

        # Remove rows where 'day_in_advance' is 'D-1' or 'D-2'
        df = df.loc[~df['day_in_advance'].isin(['D-1', 'D-2']), :]

        # Add the DataFrame to the list
        data.append(df)

    # Concatenate all DataFrames
    df = pd.concat(data, ignore_index=True)

    # Convert 'current_date' column to datetime type
    df['current_date'] = pd.to_datetime(df['current_date'], format='%d %b %Y %H:%M:%S')

    # Set the seconds and minutes to 00
    df['current_date'] = df['current_date'].apply(lambda x: x.replace(second=0, minute=0))

    # Convert datetime back to the required format
    df['current_date'] = df['current_date'].dt.strftime('%d/%m/%Y %I:%M:%S %p')

    # Save the resulting DataFrame to CSV
    df.to_csv(output_file, index=False)

    print('Combined CSV file created.')
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print("Please provide the user ID as a command-line argument.")