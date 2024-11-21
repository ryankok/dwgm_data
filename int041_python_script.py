import sys
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from urllib.parse import urljoin

def main(user_id):
    # Define the folder path based on user_id
    folder_path = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int041_files/1_input'

    url = "https://vicgas.prod.marketnet.net.au/Public_Dir/Archive"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        int041_files = []

        for link in links:
            file_url = link['href']
            if 'int041' in file_url and file_url.endswith('.csv'):
                file_name = os.path.basename(file_url)
                file_download_url = urljoin(url, file_url)
                int041_files.append(file_download_url)

        for csv_url in int041_files:
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

    directory = folder_path
    
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    data = []

    for csv_file in csv_files:
        csv_file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(csv_file_path)
        data.append(df)

    df = pd.concat(data, ignore_index=True)

    df_temp = df.drop('current_date', axis=1)
    df = df.loc[df_temp.drop_duplicates().index]

    df.rename(columns={
        "price_bod_gst_ex": "06:00:00",
        "price_10am_gst_ex": "10:00:00",
        "price_2pm_gst_ex": "14:00:00",
        "price_6pm_gst_ex": "18:00:00",
        "price_10pm_gst_ex": "22:00:00"
    }, inplace=True)

    output_file = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int041_files/2_output/int041_rawdata.csv'

    df.to_csv(output_file, index=False)
    print('Combined CSV file created.')

    df_unpivoted = pd.melt(df, id_vars=df.columns[0], value_vars=df.columns[1:6], var_name='Time', value_name='Price')
  
    df_unpivoted['date_time_identifier'] = df_unpivoted['gas_date'].astype(str) + ' ' + df_unpivoted['Time'].astype(str)
  
    output_file_unpivoted = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int041_files/2_output/DWGM_price_intervals.csv'
    df_unpivoted.to_csv(output_file_unpivoted, index=False)
    
    #print('Columns 2 to 6 unpivoted and saved to a new CSV file.')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print("Please provide the user ID as a command-line argument.")