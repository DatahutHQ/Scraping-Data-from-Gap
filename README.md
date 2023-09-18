## Web scraping ecommerce website with Python


### Overview

This Python script is designed to scrape information about men's new arrivals from the [Gap.com website](https://www.gap.com/). It utilizes powerful libraries such as Selenium and BeautifulSoup for web navigation, data extraction, and storage into a CSV file.

### Data Availability

Within the script, we use two specific labels to denote data availability:

- **'Not available'**: This label signifies that the information could not be extracted from the webpage.
- **'Not applicable'**: This label indicates that the information is not present for that particular product.

### Requirements

To run this script successfully, ensure that you have the following libraries installed:

- `selenium`: Required for browser automation and web page interaction.
- `time`: Necessary for introducing delays in the script.
- `bs4` (BeautifulSoup): Used for parsing HTML content.
- `re`: Employed for regular expression operations.
- `random`: Utilized for obtaining random numbers.
- `unicodedata`: Essential for normalizing Unicode characters.
- `pandas`: Required for manipulating tabular data.

Additionally, you'll need a compatible web driver for your browser (e.g., ChromeDriver for Google Chrome) to be used with Selenium.

### Script Overview

The script follows these key steps:

#### Importing Libraries

We import essential libraries including `pandas`, `selenium`, `time`, `bs4`, `re`, `random`, and `unicodedata`.

#### Global Constants

Constants, such as the CSV file name and URL, are defined for easy configuration.

#### Initialize WebDriver

The `initialize_driver()` function creates an instance of the WebDriver, specifically for Chrome in this case.

#### Introducing Randomness

The `random_sleep()` function adds a touch of randomness to mimic human-like behavior during web scraping.

#### Scrolling

The `scroll()` function simulates scrolling down the webpage to load more products.

#### Get BeautifulSoup Object

The `get_soup()` function extracts a BeautifulSoup object from the current page's HTML content.

#### Extracting Product Information

Various functions are defined to extract different pieces of information from the product page, including product link, type, name, prices, rating, reviews, color, available sizes, and details.

#### Main Function

The main function follows these steps:

- Initializes the WebDriver.
- Navigates to the specified URL and scrolls to load more products.
- Retrieves product elements from the main page.
- Iterates through each product, extracts information, and writes it to a CSV file.
- Cleans up and quits the WebDriver.

#### Running the Main Function

The script automatically runs the main function if executed directly.

### How to Use

Follow these steps to use the script:

1. Install the required libraries using `pip install selenium beautifulsoup4`.
2. Download and install the appropriate web driver compatible with your browser (e.g., [ChromeDriver](https://sites.google.com/chromium.org/driver/?pli=1)).
3. Run the script using a Python interpreter: `python gap.py`.
4. The script will extract information and save it to a CSV file (by default, `gap_men_new_arrivals.csv`).

### Data Files

Two CSV files are generated:

- `scraped_data.csv`: Contains the raw, unprocessed data extracted directly from the website.
- `cleaned_data.csv`: Contains data that has been refined and categorized. This includes assigning categories to products lacking a proper category and cleaning the `Rating_Count` column.

Please ensure that web scraping is performed ethically and responsibly, adhering to the website's terms of use and without causing any harm to its performance or functionality.
