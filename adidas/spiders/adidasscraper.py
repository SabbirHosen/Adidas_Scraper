import re
import time

import scrapy
from scrapy_playwright.page import PageMethod
from ..items import AdidasProductItem
import random

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
]

fake_browser_header = {
    # "upgrade-insecure-requests": "1",
    "user-agent": random.choice(user_agent_list),
    # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    # "sec-ch-ua": "\".Not/A)Brand\";v=\"99\", \"Google Chrome\";v=\"103\", \"Chromium\";v=\"103\"",
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": "\"Linux\"",
    # "sec-fetch-site": "none",
    # "sec-fetch-mod": "",
    # "sec-fetch-user": "?1",
    # "accept-encoding": "gzip, deflate, br",
    # "accept-language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7"
}


class AdidasscraperSpider(scrapy.Spider):
    name = "adidasscraper"
    allowed_domains = ["shop.adidas.jp"]
    base_url = "https://shop.adidas.jp"

    # start_urls = ["https://shop.adidas.jp/item/?gender=mens"]

    def start_requests(self):
        url = "https://shop.adidas.jp/products/IX6440/"
        # url = "https://shop.adidas.jp/item/?gender=mens&order=1&category=wear"

        # meta_data = {
        #     'playwright': True,
        #     'playwright_include_page': True,
        #     'playwright_page_methods': [
        #         PageMethod("wait_for_selector", "div.pageSelector"),
        #     ],
        #     'errback': self.errback,
        # }
        meta_data = {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [
                PageMethod("wait_for_selector", "div.inner"),
                PageMethod("evaluate", """
                                                    async () => {
                                                        await new Promise(resolve => {
                                                            let totalHeight = 0;
                                                            const distance = 50;
                                                            const timer = setInterval(() => {
                                                                const scrollHeight = document.body.scrollHeight;
                                                                window.scrollBy(0, distance);
                                                                totalHeight += distance;
                                                                if (totalHeight >= scrollHeight) {
                                                                    clearInterval(timer);
                                                                    resolve();
                                                                }
                                                            }, 50);  // Adjust scrolling speed as needed
                                                        });
                                                    }
                                                """),
                PageMethod("wait_for_timeout", 20000)
            ],
            'errback': self.errback,
        }

        yield scrapy.Request(url, headers=fake_browser_header, callback=self.extract_product_information,
                             meta=meta_data)

    async def parse(self, response, **kwargs):
        page = response.meta["playwright_page"]
        try:
            time.sleep(2)
            print("-" * 100)
            print("Extracting pagination information")
            # page = response.meta["playwright_page"]
            page_content = await page.content()
            content = scrapy.Selector(text=page_content)
            # cards = content.css("div.test-card a.image_link.test-image_link::attr(href)").getall()

            last_page_number = content.css("div.pageSelector li span.pageTotal::text").get()
            print("pagination")
            print(last_page_number)
            if last_page_number and last_page_number != "0" and last_page_number != "1":
                for i in range(1, int(last_page_number)):
                    if i == 3:
                        break
                    next_page_url = f"{response.url}&page={i}"
                    print("next page url: ", next_page_url)
                    yield scrapy.Request(next_page_url, callback=self.extract_items, meta=dict(
                        playwright=True,
                        playwright_include_page=True,
                        playwright_page_methods=[
                            PageMethod("wait_for_selector", "div.articleDisplay"),
                            # wait for 30 seconds
                            PageMethod("wait_for_timeout", 10000)
                        ],
                        errback=self.errback,
                    )
                                         )
            else:
                yield self.extract_items(response=response)
            print("-" * 100)
        except Exception as e:
            print(e)
        finally:
            page.close()

    async def extract_items(self, response, **kwargs):
        meta_data = {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [
                PageMethod("wait_for_selector", "div.inner"),
                PageMethod("evaluate", """
                                            async () => {
                                                await new Promise(resolve => {
                                                    let totalHeight = 0;
                                                    const distance = 50;
                                                    const timer = setInterval(() => {
                                                        const scrollHeight = document.body.scrollHeight;
                                                        window.scrollBy(0, distance);
                                                        totalHeight += distance;
                                                        if (totalHeight >= scrollHeight) {
                                                            clearInterval(timer);
                                                            resolve();
                                                        }
                                                    }, 50);  // Adjust scrolling speed as needed
                                                });
                                            }
                                        """),
                PageMethod("wait_for_timeout", 20000)
            ],
            'errback': self.errback,
        }
        page = response.meta["playwright_page"]
        try:
            print("Items scarping for url {0}".format(response.url))
            for i in range(5):  # make the range as long as needed
                await page.mouse.wheel(0, 1500)
                time.sleep(2)
            time.sleep(5)

            page_content = await page.content()
            content = scrapy.Selector(text=page_content)
            cards = content.css("div.test-card a.image_link.test-image_link::attr(href)").getall()
            print("*" * 100)
            print(len(cards))
            print("products url:", cards)
            for card in cards:
                product_details_url = self.base_url + card
                # print(product_details_url)
                yield scrapy.Request(product_details_url, headers=fake_browser_header, callback=self.extract_product_information,
                             meta=meta_data)
                break

            # last_page_number = content.css("div.pageSelector li span.pageTotal::text").get()
            # print("pagination")
            # print(last_page_number)
            # if last_page_number and last_page_number != "0" and last_page_number != "1":
            #     for i in range(1, int(last_page_number)):
            #         next_page = f"{response.url}&page={i}"
            #         print(next_page)
            print("*" * 100)


        except Exception as e:
            print(e)
        finally:
            await page.close()

    async def extract_product_information(self, response, **kwargs):
        item = AdidasProductItem()
        page = response.meta["playwright_page"]
        print("-" * 100)
        try:
            print("Items scarping for url {0}".format(response.url))

            # Scrolling the page to load the all the elements properly
            # for i in range(10):
            #     await page.mouse.wheel(0, 700)
            #     time.sleep(4)
            # time.sleep(10)

            page_content = await page.content()
            with open("detailsIS15401.html", "w") as f:
                f.write(page_content)
            coordinate_info = await self.extract_coordinate(page=page)

            content = scrapy.Selector(text=page_content)
            product_details_url = response.url
            image_urls = await self.extract_image_urls(response=content)
            breadcrumbs = await self.extract_breadcrumbs(response=content)
            product_category = " ".join(content.css("a.groupName span::text").getall())
            product_title = content.css("div.articleInformation h1.itemTitle::text").get().strip()
            product_price = await self.extract_price(page=page, response=content)
            product_available_sizes = content.css("ul.sizeSelectorList li button::text").getall()

            description_title = content.css("div.js-componentsTabTarget h4::text").get()

            general_description = content.css("div.inner div.description_part *::text").getall()
            general_description = " ".join(general_description)

            item_description = content.css("div.inner ul.articleFeatures *::text").getall()
            item_description = " ".join(item_description)
            size_chart = await self.extract_size_chart(response=content)
            rating = content.css(
                "div.BVRRQuickTakeCustomWrapper div.BVRRRatingNormalOutOf  span.BVRRNumber.BVRRRatingNumber::text").get()
            number_of_review = content.css(
                "div.BVRRQuickTakeCustomWrapper span.BVRRValue span.BVRRBuyAgainTotal::text").get()
            recommendation_percentage = content.css(
                "div.BVRRQuickTakeCustomWrapper .BVRRBuyAgainPercentage span::text").get()
            product_ratings = await self.extract_ratings(response=content)
            reviews = await self.extract_reviews(response=content)
            sense_of_the_size = await self.extract_sense_of_size(response=content)
            print("*" * 100)
            # print("Product details url: {0}".format(product_details_url))
            # print("Breadcrumbs: {0}".format(breadcrumbs))
            # print("image urls: {0}".format(image_urls))
            # print("Product category: {0}".format(product_category))
            # print("Product title: {0}".format(product_title))
            # print("Price value:", product_price)
            # print("Available size:", product_available_sizes)
            # print("Coordinate value:", "\n", coordinate_info)
            # print("description_title", description_title)
            # print("general_description", general_description)
            # print("item_description", item_description)
            # print("size_chart", size_chart)
            # print("rating", rating)
            # print("number_of_review", number_of_review)
            # print("product_ratings", product_ratings)
            # print("recommendation_percentage", recommendation_percentage)
            # print("reviews", reviews)
            # product_details = {
            #     "Product details url": response.url,
            #     "Breadcrumbs": breadcrumbs,
            #     "Image urls": image_urls,
            #     "Product category": product_category,
            #     "Product title": product_title,
            #     "Price value": product_price,
            #     "Available size": product_available_sizes,
            #     "Coordinate value": coordinate_info,
            #     "Description title": description_title,
            #     "General description": general_description,
            #     "Item description": item_description,
            #     "Size chart": size_chart,
            #     "Rating": rating,
            #     "Number of reviews": number_of_review,
            #     "Product ratings": product_ratings,
            #     "Recommendation percentage": recommendation_percentage,
            #     "Reviews": reviews
            # }
            #     "Product details url": response.url,
            #     "Breadcrumbs": ,
            #     "Image urls": ,
            #     "Product category": ,
            #     "Product title": ,
            #     "Price value": ,
            #     "Available size": ,
            #     "Coordinate value": ,
            #     "Description title": ,
            #     "General description": ,
            #     "Item description": ,
            #     "Size chart": ,
            #     "Rating": ,
            #     "Number of reviews": ,
            #     "Product ratings": ,
            #     "Recommendation percentage": ,
            #     "Reviews":

            item["product_url"] = response.url
            item["breadcrumbs"] = breadcrumbs
            item["image_urls"] = image_urls
            item["product_category"] = product_category
            item["product_title"] = product_title
            item["price_value"] = product_price
            item["available_sizes"] = product_available_sizes
            item["coordinate_value"] = coordinate_info
            item["description_title"] = description_title
            item["general_description"] = general_description
            item["item_description"] = item_description
            item["size_chart"] = size_chart
            item["rating"] = rating
            item["number_of_reviews"] = number_of_review
            item["recommendation_percentage"] = recommendation_percentage
            item["reviews"] = reviews
            item["product_ratings"] = product_ratings
            item["sense_of_the_size"] = sense_of_the_size
            # print(product_details)
            # print(text)
            # print(item.values())
            print("*" * 100)
            # with open(f"data.txt", "w") as text_file:
            #     text_file.write(text)
            yield item


        except Exception as e:
            print(e)
        finally:
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()

    async def extract_price(self, page, response, **kwargs):
        style_before = await page.evaluate(
            '(function() { return window.getComputedStyle(document.querySelector(".articlePrice .price-text .price-value"), ":before").getPropertyValue("content"); })()')
        style_after = await page.evaluate(
            '(function() { return window.getComputedStyle(document.querySelector(".articlePrice .price-text .price-value"), ":after").getPropertyValue("content"); })()')
        price_value = response.css('.price-value::text').get()
        # Now apply the pseudo-element content to the extracted text
        price = "".join([style_before.strip(), price_value.strip(), style_after.strip()])
        # price_value_with_pseudo = f"{style_before.strip()} {price_value.strip()} {style_after.strip()}"
        return price

    async def extract_coordinate(self, page):
        # check_for_coordinate = div.coordinate_inner div.coordinate_box li
        coordinate_div = await page.query_selector('.coordinate_inner')
        # print("*" * 100)
        # print(coordinate_div)
        coordinate_items = []

        if coordinate_div:
            li_elements = await coordinate_div.query_selector_all('li.carouselListitem')

            # Click each li element
            for li in li_elements:
                # print(li)
                await li.click()
                time.sleep(5)
                page_content = await page.content()
                content = scrapy.Selector(text=page_content)
                cordinate_item_div = content.css("div.coordinate_inner div.coordinate_item_container")
                # print("product link", cordinate_item_div.css("div.detail a::attr(href)").get())
                # print("image link", cordinate_item_div.css("div.detail img::attr(src)").get())
                # print("product title", cordinate_item_div.css("div.detail span.titleWrapper ::text").get())
                # print("product price", cordinate_item_div.css("div.detail div.mdl-price ::text").get())
                # print(content.css("div.coordinate_inner div.coordinate_item_container"))
                product_link = f'{self.base_url}{cordinate_item_div.css("div.detail a::attr(href)").get().strip()}'
                image_link = f'{self.base_url}{cordinate_item_div.css("div.detail img::attr(src)").get().strip()}'
                coordinate_details = {
                    "product_link": product_link,
                    "image_link": image_link,
                    "product_title": cordinate_item_div.css("div.detail span.titleWrapper ::text").get().strip(),
                    "product_price": cordinate_item_div.css("div.detail div.mdl-price ::text").get().strip(),
                }
                coordinate_items.append(coordinate_details)
        return coordinate_items

    async def extract_breadcrumbs(self, response):
        """
        process the breadcrumbs div and extract the breadcrumb string
        :param response: Selector containing page response
        :return:
        """
        breadcrumb_div = response.css("div.breadcrumb_wrap")
        text = " / ".join(breadcrumb_div.css("ul.breadcrumbList li:not(.back) a::text").getall())
        return text

    async def extract_image_urls(self, response):
        image_content_div = response.css("div.pdp_article_image")
        paths = image_content_div.css("div.pdp_article_image div.article_image_wrapper img::attr(src)").getall()
        urls = [f"{self.base_url}{path}" for path in paths]
        return urls

    async def extract_ratings(self, response):
        try:
            review_rating_dict = {}
            review_ratings = response.css("div.BVRRSecondaryRatingsContainer div.BVRRRatingEntry")
            for review_rating in review_ratings:
                title = review_rating.css("div.BVRRRatingHeader ::text").get().strip()
                rating = review_rating.css("div.BVRRRatingRadioImage img::attr(title)").get()
                review_rating_dict[title] = rating

            return review_rating_dict
        except Exception as e:
            print(e)
            return None

    async def extract_reviews(self, response):
        try:
            reviews = []
            review_elements = response.css("div.BVRRContentReview")
            # print(review_elements)
            if review_elements:
                for review_element in review_elements:
                    # Extract review date
                    review_date = review_element.css("div.BVRRReviewDateContainer *::text").getall()

                    # Extract review rating
                    review_rating = review_element.xpath('.//span[@class="BVRRNumber BVRRRatingNumber"]/text()').get()

                    # Extract review title
                    review_title = review_element.xpath('.//span[@class="BVRRValue BVRRReviewTitle"]/text()').get()

                    # Extract review description
                    review_description = review_element.xpath(
                        './/div[@class="BVRRReviewText"]/descendant::*/text()').getall()
                    review_description = ' '.join(review_description).strip()

                    # Extract reviewer ID
                    reviewer_id = review_element.xpath('.//span[@class="BVRRNickname"]/text()').get()

                    # Print or store the extracted information
                    data = {
                        'Date': review_date,
                        'Rating': review_rating,
                        'Review Title': review_title,
                        'Review Description': review_description,
                        'Reviewer ID': reviewer_id
                    }
                    reviews.append(data)
            return reviews
        except Exception as e:
            print(e)
            return None

    async def extract_size_chart(self, response):
        try:
            # Extracting measurement types from the first table
            measurement_types = response.css(
                '.sizeChartTable:first-child .sizeChartTRow:nth-child(n+2) .sizeChartTHeaderCell::text').extract()
            # print("measurement_types", measurement_types)

            size_table = response.css('.sizeChartTable:last-child')

            # Extract all rows from the table
            rows = size_table.css('tr.sizeChartTRow')

            # Initialize a list to store row data
            row_data = []

            # Loop through each row and extract cell data
            for row in rows:
                # Extract cell data from each row
                cells = row.css('td.sizeChartTCell span::text').extract()
                # Append cell data to row_data list
                row_data.append(cells)

            # Print or process the row data as needed
            # print("row_data", row_data)
            # print(row_data)
            # Initialize an empty dictionary to store the combined data
            combined_data = {}
            sizes = row_data[0]
            measurements = [data for data in zip(*row_data[1:])]
            # print(sizes, measurements)
            # Iterate over both lists simultaneously
            for size, measurement in zip(sizes, measurements):
                temp = {}
                for index, measurement_type in enumerate(measurement_types):
                    temp[measurement_type] = measurement[index]
                combined_data[size] = temp

            # Convert the combined data to JSON format
            # json_data = json.dumps(combined_data, indent=4, ensure_ascii=False)
            # print(json_data)
            return combined_data
        except Exception as e:
            print(e)

    async def extract_sense_of_size(self, response):
        sense_size_div = response.css("div.sizeFitBar")
        if sense_size_div:
            size_senses = response.css("div.sizeFitBar *::text").getall()
            element = sense_size_div.css('div.bar span')
            rating = 0

            # If the element is found, extract the class attribute
            if element:
                class_attribute = element.attrib['class']

                # Extract the number from the class attribute using regular expressions
                match = re.search(r'mod-marker_(\d+\_\d+)', class_attribute)

                # If there is a match, extract the number
                if match:
                    rating = match.group(1)
                sense_of_the_size = {
                    "size_senses": size_senses,
                    "rating": rating
                }
                return sense_of_the_size
