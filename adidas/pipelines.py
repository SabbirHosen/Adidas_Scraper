# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd


class AdidasPipeline:
    def process_item(self, item, spider):
        return item


class ExcelWriterPipeline:
    def __init__(self):
        self.coordinate_data = []
        self.review_data = []
        self.size_chart_data = []
        self.product_data = []

    def open_spider(self, spider):
        self.product_data = []

    def process_item(self, item, spider):
        product_id = item['product_url'].split("/")[-2]
        product_data = {
            'product_id': product_id,
            'Product Title': item['product_title'],
            'product_url': item['product_url'],
            'Product Category': item['product_category'],
            'Price': item['price_value'],
            'Number of Reviews': item['number_of_reviews'],
            'Recommendation Percentage': item['recommendation_percentage'],
            'Breadcrumbs': item['breadcrumbs'],
            'Image URLs': item['image_urls'],
            'sense_of_the_size': item['sense_of_the_size'],
            'special_function': item['special_function'],
        }
        self.product_data.append(product_data)

        size_chart_data = [{'product_id': product_id, 'Size': size, **measurements} for size, measurements
                           in item['size_chart'].items()]
        self.size_chart_data.extend(size_chart_data)

        review_data = [{'product_id': product_id, **review} for review in item['reviews']]
        self.review_data.extend(review_data)

        coordinate_data = [{'product_id': product_id, **coordinate} for coordinate in
                           item['coordinate_value']]
        self.coordinate_data.extend(coordinate_data)

        return item

    def close_spider(self, spider):
        product_df = pd.DataFrame(self.product_data)
        size_chart_df = pd.DataFrame(self.size_chart_data)
        review_df = pd.DataFrame(self.review_data)
        coordinate_df = pd.DataFrame(self.coordinate_data)

        with pd.ExcelWriter('data.xlsx') as writer:
            product_df.to_excel(writer, sheet_name='Product Details', index=False)
            size_chart_df.to_excel(writer, sheet_name='Size Chart', index=False)
            review_df.to_excel(writer, sheet_name='Reviews', index=False)
            coordinate_df.to_excel(writer, sheet_name='Coordinate Value', index=False)

        print("Data written to Excel successfully.")
