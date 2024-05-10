import time

import scrapy
from scrapy_playwright.page import PageMethod


class AdidasscraperSpider(scrapy.Spider):
    name = "adidasscraper"
    allowed_domains = ["shop.adidas.jp"]
    base_url = "https://shop.adidas.jp"

    # start_urls = ["https://shop.adidas.jp/item/?gender=mens"]

    def start_requests(self):
        url = "https://shop.adidas.jp/products/IS1413/"
        # url = "https://shop.adidas.jp/item/?gender=mens"
        yield scrapy.Request(url, callback=self.extract_product_information, meta=dict(
            playwright=True,
            playwright_include_page=True,
            playwright_page_methods=[
                PageMethod("wait_for_selector", "div.inner"),
                # PageMethod("wait_for_selector", "div.articleDisplay"),
                # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                # PageMethod("evaluate",
                #            "for (let i = 0; i < 8; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                # wait for 30 seconds
                PageMethod("wait_for_timeout", 10000)
                # PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
            ],
            errback=self.errback,
        ))

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
                            # PageMethod("wait_for_selector", "div.articleDisplay"),
                            # PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                            # PageMethod("evaluate",
                            #            "for (let i = 0; i < 8; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
                            # wait for 30 seconds
                            PageMethod("wait_for_timeout", 10000)
                            # PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
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
            # print("products url:", cards)
            for card in cards:
                product_details_url = self.base_url + card
                print(product_details_url)
                yield {"product_details_url": product_details_url}

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
        page = response.meta["playwright_page"]
        try:
            print("Items scarping for url {0}".format(response.url))
            for i in range(5):  # make the range as long as needed
                await page.mouse.wheel(0, 1500)
                time.sleep(2)
            time.sleep(10)
            style_before = await page.evaluate(
                '(function() { return window.getComputedStyle(document.querySelector(".articlePrice .price-text .price-value"), ":before").getPropertyValue("content"); })()')
            style_after = await page.evaluate(
                '(function() { return window.getComputedStyle(document.querySelector(".articlePrice .price-text .price-value"), ":after").getPropertyValue("content"); })()')
            # Now apply the pseudo-element content to the extracted text


            page_content = await page.content()
            # with open("details.html", "w") as f:
            #     f.write(page_content)

            content = scrapy.Selector(text=page_content)

            text = content.css("script#__NEXT_DATA__::text").get()
            price_value = response.css('.price-value::text').get()
            price_value_with_pseudo = f"{style_before.strip()} {price_value.strip()} {style_after.strip()}"
            print("*" * 100)
            print("Price value with pseudo-elements:", price_value_with_pseudo)
            print(text)
            print("*" * 100)
            # with open(f"data.txt", "w") as text_file:
            #     text_file.write(text)


        except Exception as e:
            print(e)
        finally:
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
