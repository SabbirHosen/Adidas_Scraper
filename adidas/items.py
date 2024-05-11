# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AdidasProductItem(scrapy.Item):
    product_url = scrapy.Field()
    breadcrumbs = scrapy.Field()
    image_urls = scrapy.Field()
    product_category = scrapy.Field()
    product_title = scrapy.Field()
    price_value = scrapy.Field()
    available_sizes = scrapy.Field()
    coordinate_value = scrapy.Field()
    description_title = scrapy.Field()
    general_description = scrapy.Field()
    item_description = scrapy.Field()
    size_chart = scrapy.Field()
    rating = scrapy.Field()
    number_of_reviews = scrapy.Field()
    recommendation_percentage = scrapy.Field()
    reviews = scrapy.Field()
    product_ratings = scrapy.Field()
    sense_of_the_size = scrapy.Field()
    special_function = scrapy.Field()
