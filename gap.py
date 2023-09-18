# importing required libraries
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import re
import random
import unicodedata
import pandas as pd

"""
inside the code we have used 'Not available' in some places and 'Not applicable' in some places
'Not available' means that the information could not be extracted from the page
'Not applicable' means that the information is not present for that product
"""

# Global Constants
# output csv file name
CSV_FILENAME = 'gap_men_new_arrivals.csv'
# PLP stands for Product Listing Page
# It is the page in which the list of products is available 
PLP_URL = "https://www.gap.com/browse/category.do?cid=11900&department=75"


# Initialize the WebDriver
def initialize_driver():
    """
    return: WebDriver instance (Chrome in this case)
    """
    driver = webdriver.Chrome()
    return driver

# Random sleep to mimic human behavior
def random_sleep(min_time=4, max_time=7):
    """
    here uniform function is used which takes decimal values as well and not just whole numbers
    thus showing somewhat more natural human behavior

    :param min_time: minimum time to sleep, default value is 4
    :param max_time: maximum time to sleep, default value is 7

    delays program execution for a random amount of time between min_time and max_time
    we use a range of 4-7 seconds as selenium sometimes requires quite a bit of time to load the page
    """
    sleep_time = random.uniform(min_time, max_time)
    sleep(sleep_time)

# Scroll down the page to load more products
def scroll(driver, times=1):
    """
    our target site is a responsive site with infinite scrolling
    infinite scrolling is a technique where the page keeps on loading more content as the user scrolls down
    this is done to avoid pagination and to provide a seamless user experience
    thus we need to scroll down the page to load more products

    our function executes in such a way that after going to the bottom of a page we then go to the middle
    this is done in case some elements were returned
    
    here we are using javascript to scroll down to various parts of the page

    :param driver: WebDriver instance
    :param times: number of times to scroll down the page, default value is 1

    """

    execution_count = 0
    while execution_count < times:
        random_sleep()
        # bottom
        driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)"
            ) 
        random_sleep()
        # middle
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight / 2)"
            ) 
        execution_count += 1
    # top
    driver.execute_script(
        "window.scrollTo(0, 0)"
        ) 
    random_sleep()
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight / 2)"
        )
    random_sleep()
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)"
        )

# Get BeautifulSoup object from the current page
def get_soup(driver):
    """
    :param driver: WebDriver instance
    :return: BeautifulSoup object
    """
    return BeautifulSoup(driver.page_source, 'lxml')

# Extract product url from a product element
def extract_pdp_url(product):
    """
    pdp stands for product description page
    it is the page in which the whole information about the product is present 
    product url is present in the form - 'https://www.gap.com/browse/product.do?pid=774933022&cid=11900&pcid=11900&vid=1&nav=meganav%3AMen%3AJust%20Arrived%3ANew%20Arrivals&cpos=116&cexp=2859&kcid=CategoryIDs%3D11900&ctype=Listing&cpid=res23090805504869997736471#pdp-page-content'
    we need to extract the part till the value of pid (inclusive)
    the rest of the url is not needed and can even break the url at a later date    

    :param product: product element
    :return: pdp url which is a string
    """

    try:
        url = product.find('a').get('href')
        url = url.split('&')[0]
    except:
        url = 'Not available'
    return url

# Extract product type from the product page
def extract_product_type(soup):
    """
    the div with class pdp-mfe-1atmbpz contains the two a tags
    the first a tag contains the product section - men, women, boys, baby
    the second a tag contains the product type - jeans, t-shirts, shirts, etc.
    we need to extract the second a tag

    :param soup: BeautifulSoup object
    :return: product type which is a string    
    """

    try:
        product_type_element = soup.find('div', 
                                         class_='pdp-mfe-1atmbpz'
                                         )
        product_type_a = product_type_element.find_all('a')
        product_type = product_type_a[1].get_text() 
    except:
        product_type = 'Not available'
    return product_type

# Extract product name from the product page
def extract_product_name(soup):
    """
    the h1 tag which contains the product has a different class name for each product
    but every h1 tag has the class name starting with pdp-mfe-

    :param soup: BeautifulSoup object
    :return: product name which is a string
    """
    try:
        product_name_element = soup.select('h1[class^="pdp-mfe-"]') 
        product_name = product_name_element[0].text
    except:
        product_name = 'Not available'
    return product_name

# Extract product prices from the product page
def extract_prices(soup):
    """
    the price is present in the div with class pdp-pricing pdp-mfe-1x0pbuu
    the price element can contain either a single price or two prices
    when the selling price and max retail price are different, then there are two prices in the price element

    selling price element exists only if the selling price and max retail price are different
    otherwise the price element contains only a single price and that is taken as the selling price
    max retail price element exists only if the selling price and max retail price are different
    otherwise the selling price is taken as the max retail price

    re library is used to remove any text within parentheses

    :param soup: BeautifulSoup object
    :return: selling price and max retail price which are strings    
    """

    try:
        price_element = soup.find('div', class_='pdp-pricing pdp-mfe-1x0pbuu')
        selling_price_element = price_element.find('span', class_='pdp-pricing--highlight pdp-pricing__selected pdp-mfe-1x0pbuu')
        if selling_price_element:
            selling_price = selling_price_element.text.strip('$')
        else:
            selling_price = price_element.text.strip('$')
        selling_price = re.sub(r'\([^()]*\)', '', selling_price).strip()  

        max_retail_price_element = price_element.find('span', class_='product-price__strike pdp-mfe-eyzase')
        if max_retail_price_element:
            max_retail_price = max_retail_price_element.text.strip('$')
        else:
            max_retail_price = selling_price 
    except:
        selling_price = 'Not available'
        max_retail_price = 'Not available'
    return selling_price, max_retail_price


# Extract product rating from the product page
def extract_star_value(soup):
    """
    the span with class pdp-mfe-3jhqep contains the star rating in the form - 5 stars, x are filled
    we need to extract the value of x

    :param soup: BeautifulSoup object
    :return: star value which is a string
    """

    try:
        star_value = soup.find('span', class_='pdp-mfe-3jhqep').text
        star_value = star_value.split(',')[1].split(' ')[1]
    except:
        star_value = 'Not available'
    return star_value

# Extract the number of product ratings from the product page
def extract_ratings_count(soup):
    """
    the div with class pdp-mfe-17iathi contains the number of ratings in the form - x ratings
    we need to extract the value of x

    :param soup: BeautifulSoup object
    :return: ratings count which is a string
    """

    try:
        ratings_count = soup.find('div', class_='pdp-mfe-17iathi').text
        ratings_count = ratings_count.split(' ')[0]
    except:
        ratings_count = 'Not available'
    return ratings_count

# Extract product color from the product page
def extract_color(soup):
    """
    the span with class swatch-label__value contains the color of the product

    :param soup: BeautifulSoup object
    :return: color which is a string
    """
    try:
        color = soup.find('span', class_='swatch-label__value').text
    except:
        color = 'Not available'
    return color

# Extract available sizes from the product page
def extract_available_sizes(soup):
    """
    the div with class pdp-mfe-17f6z2a pdp-dimension pdp-dimension--should-display-redesign-in-stock contains the available sizes
    the available sizes are stored into a list

    in cases where there is no size available, the div with class pdp-mfe-17f6z2a pdp-dimension pdp-dimension--should-display-redesign-in-stock is not present
    in such cases we return a list with 'Not applicable' as the only element
    this can be seen in case of accessories such as bags

    :param soup: BeautifulSoup object
    :return: available sizes which is a list
    """
    try:
        available_sizes_element = soup.find_all('div', class_='pdp-mfe-17f6z2a pdp-dimension pdp-dimension--should-display-redesign-in-stock')
        available_sizes = []
        for size in available_sizes_element:
            available_sizes.append(size.text)
    except:
        available_sizes = ['Not available']
    if not available_sizes:
        available_sizes = ['Not applicable']
    return available_sizes

# Extract product details from the product page
def extract_details(soup):
    """
    the product details are present in the form of a list
    there are three sets of details - fit and sizing, product details, fabric and care
    each set of details is present in a ul tag with class name starting with product-information-item__list
    the text obtained is then normalized to remove any unicode characters
    normalizing means converting the special characters to their normal form
    in our case we can particularly see zero width space characters (u200b) in the text 

    :param soup: BeautifulSoup object
    :return: fit and sizing, product details, fabric and care which are lists
    """

    try:
        details_elements = soup.select('ul[class^="product-information-item__list"]')
        if len(details_elements) == 3:
            fit_sizing_element = details_elements[0].find_all('li')
            fit_sizing = []
            for detail in fit_sizing_element:
                if 'wearing' not in detail.text:
                    text = unicodedata.normalize("NFKD", detail.text).rstrip('. ')
                    fit_sizing.append(text)

            product_details_element = details_elements[1].find_all('li')
            product_details = []
            for detail in product_details_element:
                if '#' not in detail.text and  'P.A.C.E.' not in detail.text and 'pace' not in detail.text:
                    text = unicodedata.normalize("NFKD", detail.text).rstrip('.')
                    product_details.append(text)

            fabric_care_element = details_elements[2].find_all('li')
            fabric_care = []
            for detail in fabric_care_element:
                text = unicodedata.normalize("NFKD", detail.text).rstrip('. ')
                fabric_care.append(text)

        else:
            fit_sizing = ['Not applicable']
            
            product_details_element = details_elements[0].find_all('li')
            product_details = []
            for detail in product_details_element:
                if '#' not in detail.text and 'P.A.C.E.' not in detail.text and 'pace' not in detail.text:
                    text = unicodedata.normalize("NFKD", detail.text).rstrip('.')
                    product_details.append(text)
            
            fabric_care_element = details_elements[1].find_all('li')
            fabric_care = []
            for detail in fabric_care_element:
                text = unicodedata.normalize("NFKD", detail.text).rstrip('. ')
                fabric_care.append(text)
    except:
        fit_sizing = ['Not available']
        product_details = ['Not available']
        fabric_care = ['Not available']
    
    return [fit_sizing, product_details, fabric_care]



# Main function
def main():
    """
    begins with initializing the WebDriver
    then goes to the PLP_URL
    - PLP means product listing page and it is the page in which the list of products is available

    then scrolls down the page to load more products
    then gets the BeautifulSoup object from the current page
    then gets each product element from the main page
    then extracts the product url from each product element and stores it in a list
    then initializes a pandas dataframe with the required columns
    then iterates through each product and extracts information
    then stores the information in the initialized pandas dataframe
    then prints the progress, which is the count of the current product
    after going through every url writes the dataframe to the CSV file
    then quits the WebDriver

    in the above description each line corresponds to each section of the main function which is seperated by a blank line
    """
    driver = initialize_driver()
    driver.get(PLP_URL)

    scroll(driver, times=4)

    soup = get_soup(driver)
    product_info = soup.find_all('div', class_='category-page-1wcebst')

    pdp_url_list = []
    for product in product_info:
        pdp_url = extract_pdp_url(product)
        pdp_url_list.append(pdp_url)

    df = pd.DataFrame(columns=
                      ['Product_URL', 'Product_Type', 'Product_Name',
                       'Selling_Price', 'Max_Retail_Price', 'Rating', 
                       'Rating_Count', 'Color', 'Available_Sizes', 
                       'Fit_Sizing', 'Product_Details', 'Fabric_Care']
                       )
        
    for index, pdp_url in enumerate(pdp_url_list, start=1):
        if pdp_url != 'Not available':
            driver.get(pdp_url)
            random_sleep()
            soup = get_soup(driver)
            product_type = extract_product_type(soup)
            product_name = extract_product_name(soup)
            selling_price, max_retail_price = extract_prices(soup)
            star_value = extract_star_value(soup)
            ratings_count = extract_ratings_count(soup)
            color = extract_color(soup)
            available_sizes = extract_available_sizes(soup)
            details = extract_details(soup)

            df.loc[index] = [
                pdp_url, product_type, product_name, 
                selling_price, max_retail_price, star_value, 
                ratings_count, color, ', '.join(available_sizes), 
                ', '.join(details[0]), ', '.join(details[1]), 
                ', '.join(details[2])
                ]

            print(index)

    df.to_csv(CSV_FILENAME, index=False)
    print(f"Data written to {CSV_FILENAME}")
    driver.quit()


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
