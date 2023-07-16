import os
import requests
import zipfile

#Here we extract the zip file from a link on CCP's webpage, 
#this zip file is then extracted into a folder called 'extracted_data'

def download_and_extract_zip(url):
    response = requests.get(url)
    if response.status_code == 200:
        zip_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.zip')
        with open(zip_file_path, 'wb') as file:
            file.write(response.content)
            print('Zip file downloaded successfully.')

        extraction_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extracted_data')
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
            print('Zip file extracted successfully.')
    else:
        print('Failed to download the zip file.')

def generate_monthly_url(month):
    url_template = "https://web.ccpgamescdn.com/aws/community/EVEOnline_MER_{}.zip"
    return url_template.format(month)

# Prompt the user to enter the month
month = input("Enter the month as 'Month20XX' (e.g. 'Mar2023'): ")

# Generate the monthly URL based on user input
url = generate_monthly_url(month)
download_and_extract_zip(url)
