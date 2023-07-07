import os
import requests
from bs4 import BeautifulSoup
import wget

def master_theses_scraper(url, down_dir, headers):
    """
    Scrapes master's theses from a specified URL, retrieves download links, and downloads the theses.

    Args:
        url (str): The URL of the webpage containing the LvB theses.
        down_dir (str): The directory where the scraped PDFs will be downloaded.
        headers (dict): HTTP headers to be used in the requests.

   
    """

    # Makes the directory in case it does not exist already
    os.makedirs(down_dir, exist_ok=True)

    # Get the response from the URL
    response = requests.get(url)

    # Set up the soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the container that holds the hyperlinks
    link_container = soup.find('div', id='parent-fieldname-text', class_="")

    # Get all the links in the container, under <a> in the HTML code
    links = link_container.find_all('a')
    print('Scraping complete.')
    print(f'{len(links)} entries found.')
    print('An example entry in our links container looks like:\n', links[0])
    print('\n')
    
    print('Identifying invalid links...')
    # Set up empty container for the unusable link
    remove_from_list = []

    # For loop to identify invalid links
    for link in links:
        # Strips all text in our entries besides the URL
        href = link.get('href')
        remove_link = requests.get(href)

        # Checks for 404 status
        if remove_link.status_code == 404:
            remove_from_list.append(link)
            continue

    print(f'{len(remove_from_list)} invalid links identified.')

    # Use list comprehension to drop the 404 links
    valid_links = [link for link in links if link not in remove_from_list]

    print(f'{len(valid_links)} entries remain.')

    print('Identifying Master\'s Theses...')
    # Set up a new empty container for links to the master's papers
    master_links = []
    master_dates = []
    for link in valid_links:
        link_r = requests.get(link['href'])
        link_s = BeautifulSoup(link_r.content, 'html.parser')

        # After manually inspecting the HTML, it can be seen that <span> objects with class = type contain info on whether the paper is a Master's thesis or other type of work
        # Define the span with class 'type'
        type_span = link_s.find('span', class_='type')
        date_span = link_s.find('span', class_="date")

        # Look if the object includes 'Masterarbeit' as text
        if type_span and type_span.text == 'Masterarbeit':
            master_links.append(link)
            master_dates.append(date_span.text)

    print(f'{len(master_links)} Master\'s Theses identified.')
    print('A sample entry looks as follows:\n', master_links[0])

    print('Retrieving download links...')

    # Set up base_url to concatenate with the individual download links
    base_url = 'https://edoc.hu-berlin.de'

    # An empty container for the download links
    dl_links = []
    dl_dates = []

    for link in master_links:
        # Strips the entry shown above to retain only the link to the abstract pages
        thesis_url = link['href']

        # Gets response from the abstract pages
        thesis_url_response = requests.get(thesis_url, headers=headers)

        # Parses the abstract pages
        thesis_url_soup = BeautifulSoup(thesis_url_response.content, 'html.parser')

        # Find the download link on the abstract pages (variable named meta because ran out of name ideas)
        meta = thesis_url_soup.find('a', class_='clearfix')

        # Filter for missing download links
        if meta is not None and 'href' in meta.attrs:
            # Strip the entries to only keep the link
            dl_link = meta['href']
            # Concatenate with base URL
            dl_links.append(base_url + dl_link)
            dl_dates.append(master_dates[master_links.index(link)])
            
        else:
            print(f"Due to missing link, dropped entry: {link}")

    print('Retrieval complete.')

   
    print('Checking if all download links accessible...') # Essentially an optional step that just looks cool but actually takes too much time

    for link in dl_links:
        verify_response = requests.get(link)
        if response.status_code != 200:
            print(f'Link {link} is not working.')

    print('All done!')
    print('An example of our link looks like:\n', dl_links[0])
    print(f'We can download {len(dl_links)} Master\'s Theses in total.')

    print('Download in progress...')

    # Using enumerate, our filenames will be numbered
    for index, link in enumerate(dl_links, start=1):
        # {index} takes the number of the file assigned by enumerate
        # Rest of the code grabs the title from the download URL
        filename = f"{index}.{link.split('/')[-1].split('?')[0]}_{dl_dates[index-1]}.pdf"
        # Specifies download path
        file_path = os.path.join(down_dir, filename)
        # Downloads
        try:
            wget.download(link, out=file_path)
        # We should not expect any errors, but just in case
        except Exception as e:
            print(f'Failed to download file: {filename}. Error: {str(e)}')

    print('Download Complete')
