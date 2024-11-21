import sys
import requests
import zipfile
import io
import pandas as pd
import os

def main(user_id):
    
    url = "https://nemweb.com.au/Reports/Current/GBB/GasBBActualFlowStorageLast31.CSV"
    url_master = "https://nemweb.com.au/Reports/Current/GBB/GasBBActualFlowStorage.zip"
    input_directory = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/gas_flow_cap_outlook_files/1_input'
    output_directory = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/gas_flow_cap_outlook_files/2_output'

    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)

    # Download the CSV file from url to input directory
    response_csv = requests.get(url)
    if response_csv.status_code == 200:
        with open(os.path.join(input_directory, 'GasBBActualFlowStorageLast31.csv'), 'wb') as file:
            file.write(response_csv.content)
        print(f"CSV file downloaded successfully to {input_directory}")

    # Download and extract the ZIP file from url_master to input directory
    response_master = requests.get(url_master)
    if response_master.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response_master.content), 'r') as zip_ref:
            zip_ref.extractall(input_directory)
        print(f"ZIP file extracted successfully to {input_directory}")

    # Read the CSV files
    master_data = pd.read_csv(os.path.join(input_directory, 'GasBBActualFlowStorage.CSV'))
    appended_data = pd.read_csv(os.path.join(input_directory, 'GasBBActualFlowStorageLast31.csv'))

    # Append the data and remove duplicates
    new_dataframe = pd.concat([master_data, appended_data], ignore_index=True)
    new_dataframe.drop_duplicates(subset=[col for col in new_dataframe.columns if col != 'LastUpdated'], inplace=True)

    # Save the new CSV to the output directory
    new_csv_path = os.path.join(output_directory, "GasBBActualFlowStorageMASTERFILE.csv")
    new_dataframe.to_csv(new_csv_path, index=False)
    print(f"New CSV saved to {new_csv_path}")  

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print("Please provide the user ID as a command-line argument.")