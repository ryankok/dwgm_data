import requests
import sys
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
import win32com.client

def main(user_id):
    # Define the folder path based on user_id
    folder_path = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int037b_files/1_input'

    url_list = ["https://vicgas.prod.marketnet.net.au/Public_Dir/Archive", "https://vicgas.prod.marketnet.net.au/Public_Dir/"]

    for url in url_list:
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            int037b_files = []
            
            for link in links:
                file_url = link['href']
                
                if 'int037b' in file_url and file_url.endswith('.csv'):  # Filter int037b CSV files
                    file_name = os.path.basename(file_url)
                    file_download_url = urljoin(url, file_url)  # Construct the absolute URL
                    int037b_files.append(file_download_url)
            
            for csv_url in int037b_files:
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
                # else:
                #     print(f'Skipped download - File already exists: {file_path}')
        else:
            print(f'Failed to access the URL: {url}')    

    # Paths to the directory and output files
    directory = folder_path
    output_file = f'C:/Users/{user_id}/Woodside Energy Ltd/East Coast Domestic Gas Team - Documents/Analysis/Automations/int037b_files/2_output/int037b_raw_data.csv'

    # List the CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # List to store the loaded data
    data = []

    # Iterate through each CSV file and load the data
    for csv_file in csv_files:
        csv_file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(csv_file_path)

        # Add the DataFrame to the list
        data.append(df)

    # Concatenate all DataFrames
    df = pd.concat(data, ignore_index=True)

    # Drop the 'current_date' column, temporarily for deduplication
    df_temp = df.drop('current_date', axis=1)

    # Drop duplicate rows disregarding 'current_date'
    df = df.loc[df_temp.drop_duplicates().index]

    # Convert 'approval_datetime' column to datetime type
    df['approval_datetime'] = pd.to_datetime(df['approval_datetime'], format='%d %b %Y %H:%M:%S')

    # Set the seconds and minutes to 00
    df['approval_datetime'] = df['approval_datetime'].apply(lambda x: x.replace(second=0, minute=0))

    # Convert datetime back to the required format
    df['approval_datetime'] = df['approval_datetime'].dt.strftime('%d-%m-%Y %I:%M:%S %p')

    # Convert 'approval_datetime' column to 24-hour format
    df['approval_datetime'] = pd.to_datetime(df['approval_datetime'], format='%d-%m-%Y %I:%M:%S %p').dt.strftime('%d-%m-%Y %H:%M:%S')

    # Save the DataFrame to CSV
    df.to_csv(output_file, index=False)

    print('Combined CSV has been created!')

    # Assuming you have previously defined df and imported the necessary libraries

    # Convert 'gas_date' column to datetime type
    df['gas_date'] = pd.to_datetime(df['gas_date'])
    df['approval_datetime'] = pd.to_datetime(df['approval_datetime'])

    # Filter data for today's approval_datetime, and gas_date for today and tomorrow
    today_approval_datetime = pd.Timestamp.now().normalize()
    tomorrow = today_approval_datetime + pd.DateOffset(days=1)
    df_filtered_today = df[
        (df['approval_datetime'].dt.date == today_approval_datetime.date()) & 
        (
            (df['gas_date'].dt.date == today_approval_datetime.date()) |
            (df['gas_date'].dt.date == tomorrow.date())
        ) &
        (~df['approval_datetime'].isnull())
    ]

    if not df_filtered_today.empty:
        # Pivot the filtered data based on 'demand_type_name' and 'gas_date'
        pivot_df_today = df_filtered_today.pivot(index='approval_datetime', columns=['demand_type_name','gas_date'], values='price_value_gst_ex')

        # Reset index to make 'approval_datetime' a column
        pivot_df_today.reset_index(inplace=True)

        # Create headers for the table with demand_type_name and gas_date
        headers = []
        for col in pivot_df_today.columns:
            demand_type_name, gas_date = col
            if pd.isnull(gas_date):
                headers.append(f"{demand_type_name}")
            else:
                formatted_date = gas_date.strftime('%d %b %y').replace(' 0', ' ')
                headers.append(f"{demand_type_name} - {formatted_date}")

        pivot_df_today.columns = headers
        
        # Print the formatted table with centered values
        print(tabulate(pivot_df_today, headers='keys', tablefmt='pretty', stralign='center',showindex=False))
    else:
        print("No data available for today's approval_datetime and gas_date for today and tomorrow")

    html_table = tabulate(pivot_df_today, headers='keys', tablefmt='html', showindex=False)

    # Add CSS styling for borders, center alignment, and bold headers
    html_table037b = f'<style>table, th, td {{ font-size: 18px; border: 1px solid black; border-collapse: collapse; padding: 8px; text-align: center; }}</style>\n{html_table}'

    # Bold the headers by wrapping them in <b> tags
    html_table037b = html_table037b.replace('<th>', '<th style="font-weight:bold">')

    # Get the latest date (index label) from the DataFrame index
    latest_current_date = pivot_df_today['approval_datetime'].max().strftime('%d-%m-%Y %H:%M:%S')

    # Define the path to the folder where the CSV files are downloaded
    path_folder = directory

    # Get the list of downloaded file paths in the path_folder
    downloaded_files = [os.path.join(path_folder, filename) for filename in os.listdir(path_folder) if filename.endswith(".csv")]

    # Determine the path to the most recently downloaded CSV file
    latest_csv_file = max(downloaded_files, key=os.path.getctime)

    # Set up Outlook application and send email as described in the original code snippet
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    # Add recipient, subject with the latest current date, and body with the table embedded in HTML
    recipient_email = "bhp.eagas@woodside.com"
    cc_emails = ["edward.gurango@woodside.com", "paul.papageorgiou@woodside.com", "elizabeth.valters@woodside.com", "ryan.kok@woodside.com"]

    mail.To = recipient_email
    mail.CC = ";".join(cc_emails)  # Combine multiple CC emails separated by a semicolon
    mail.Subject = f"DWGM Intraday Price Sensitivity for {latest_current_date}"
    mail.HTMLBody = f"<html><body><p>Please find the summary table for DWGM below:</p>{html_table037b}</body></html>"

    # Attach the latest downloaded CSV file to the email
    attachment = mail.Attachments.Add(Source=latest_csv_file)

    # Set the sender email address to bhp.eagas@woodside.com
    mail.SentOnBehalfOfName = "bhp.eagas@woodside.com"

    # Send the email
    mail.Send()

    print('Email has been sent!')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_id = sys.argv[1]
        main(user_id)
    else:
        print("Please provide the user ID as a command-line argument.")