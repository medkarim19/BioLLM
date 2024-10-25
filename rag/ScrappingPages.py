import requests
from bs4 import BeautifulSoup

# Base URL
base_url = 'https://phys.org/biology-news/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_page(url):
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return [], None
    
    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all h3 elements with the specified class
    h3_elements = soup.find_all('h3', class_='mb-1 mb-lg-2')
    
    # Extract the href attribute from each a tag within the h3 elements
    hrefs = [h3.find('a')['href'] for h3 in h3_elements if h3.find('a')]
    
    # Find the "Load more" button and get the URL for the next page
    load_more = soup.find('a', class_='btn btn-lg btn-outline-secondary text-low-up')
    next_page_url = load_more['href'] if load_more else None
    
    return hrefs, next_page_url

# Start scraping from the base URL
current_page_url = base_url
all_hrefs = []

for page_number in range(1, 4):  # Loop through pages 1 to 3
    print(f"Scraping page {page_number}: {current_page_url}")
    hrefs, next_page_url = scrape_page(current_page_url)
    all_hrefs.extend(hrefs)
    
    if not next_page_url:
        break
    
    # Construct the full URL for the next page
    current_page_url = requests.compat.urljoin(base_url, next_page_url)

# Print all the extracted hrefs
for href in all_hrefs:
    print(href)
