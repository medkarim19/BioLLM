import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://phys.org/biology-news/'

# Define headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Send a GET request to the URL with headers
response = requests.get(url, headers=headers)

# Check the response status code
if response.status_code != 200:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
else:
    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all h3 elements with the specified class
    h3_elements = soup.find_all('h3', class_='mb-1 mb-lg-2')

    if not h3_elements:
        print("No <h3> elements found with the specified class.")
    else:
        # Extract the href attribute from each a tag within the h3 elements
        hrefs = [h3.find('a')['href'] for h3 in h3_elements if h3.find('a')]

        # Print the extracted hrefs
        if not hrefs:
            print("No hrefs found within the <h3> elements.")
        else:
            for href in hrefs:
                print(href)
