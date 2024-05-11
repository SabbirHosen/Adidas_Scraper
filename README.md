# Adidas Scraper

This project is a web scraper built using Scrapy to extract product information from the Adidas Japan website (https://shop.adidas.jp/). It extracts details such as product titles, prices, images, sizes, reviews, and more.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/SabbirHosen/Adidas_Scraper.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Adidas_Scraper
   ```

3. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```
6. Install the specific browser(s) that in scrapy `chromium`:

   ```bash
   playwright install chromium
   ```

## Usage

1. Run the Scrapy spider to start scraping product data:

   ```bash
   scrapy crawl adidasscraper
   ```

   This will start the scraping process and save the extracted data to an Excel file named `product_data.xlsx`.

## Excel Output

The scraped data is saved in an Excel file with four sheets, each containing specific information:

- **Product Details**: Contains general product information such as product title, category, price, number of reviews, etc.
- **Size Chart**: Provides details about available sizes for each product.
- **Reviews**: Includes customer reviews for each product, along with ratings and review descriptions.
- **Coordinate Value**: Displays coordinate information for each product.

## Dependencies

- [Scrapy](https://scrapy.org/) - A web crawling and web scraping framework for Python.
- [Pandas](https://pandas.pydata.org/) - A fast, powerful, flexible, and easy-to-use open-source data analysis and manipulation tool.
- [Playwright](https://playwright.dev/) - A tool for automating browsers.

## Contact Information
- Name: Sabbir Hosen
- Email: [contact.sabbirhosen@gmail.com](mailto:contact.sabbirhosen@gmail.com)
- LinkedIn: [https://www.linkedin.com/in/sabbirhosen00/](https://www.linkedin.com/in/sabbirhosen00/)
