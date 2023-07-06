import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape product details from a product element
def scrape_product(product):
    product_url = product.find('a', {'class': 'a-link-normal s-no-outline'})['href']
    product_name = product.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
    product_price = product.find('span', {'class': 'a-price-whole'}).text.strip()
    product_rating = product.find('span', {'class': 'a-icon-alt'}).text.strip().split()[0]
    review_count_element = product.find('span', {'class': 'a-size-base'})
    product_review_count = review_count_element.text.strip().split()[0] if review_count_element else '0'
    
    # Scrape additional details from the product's URL
    product_details = scrape_product_details(product_url)
    
    # Create a dictionary of the product data
    product_data = {
        'URL': product_url,
        'Name': product_name,
        'Price': product_price,
        'Rating': product_rating,
        'Review Count': product_review_count,
        'Description': product_details.get('description', ''),
        'ASIN': product_details.get('asin', ''),
        'Product Description': product_details.get('product_description', ''),
        'Manufacturer': product_details.get('manufacturer', '')
    }
    
    return product_data

# Function to scrape additional details from a product's URL
def scrape_product_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        description = soup.find('div', {'id': 'productDescription'}).text.strip() if soup.find('div', {'id': 'productDescription'}) else ''
        asin = soup.find('th', text='ASIN').find_next_sibling('td').text.strip() if soup.find('th', text='ASIN') else ''
        product_description = soup.find('div', {'id': 'aplus'}).text.strip() if soup.find('div', {'id': 'aplus'}) else ''
        manufacturer = soup.find('a', {'id': 'bylineInfo'}).text.strip() if soup.find('a', {'id': 'bylineInfo'}) else ''
        
        product_details = {
            'description': description,
            'asin': asin,
            'product_description': product_description,
            'manufacturer': manufacturer
        }
        
        return product_details
    else:
        return {}

# Scrape multiple pages of product listings
base_url = 'https://www.amazon.in/s'
product_data_list = []

for page in range(1, 21):
    params = {
        'k': 'bags',
        'crid': '2M096C61O4MLT',
        'qid': '1653308124',
        'sprefix': 'ba%2Caps%2C283',
        'ref': f'sr_pg_{page}',
        'page': page
    }
    
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_list = soup.find_all('div', {'data-component-type': 's-search-result'})

        for product in product_list:
            product_data = scrape_product(product)
            product_data_list.append(product_data)
            
    else:
        print(f'Failed to retrieve page {page}')

# Convert the product data list to a DataFrame
df = pd.DataFrame(product_data_list)

# Export the data to a CSV file
df.to_csv('product_data.csv', index=False)