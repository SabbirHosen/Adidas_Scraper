import json

from scrapy import Selector


def extract_breadcrumbs(breadcrumb_div):
    """
    process the breadcrumbs div and extract the breadcrumb string
    :param breadcrumb_div: Selector containing breadcrumbs div
    :return:
    """
    text = " / ".join(breadcrumb_div.css("ul.breadcrumbList li:not(.back) a::text").getall())
    return text


def extract_image_urls(image_div):
    urls = image_div.css("div.pdp_article_image div.article_image_wrapper img::attr(src)").getall()
    return urls

def extract_size_chart(size_table):
    rows = size_table.css('div.sizeChart table.sizeChartTable tbody tr')

    # Initialize dictionary to store size chart data
    size_chart_data = {}

    # Iterate over rows
    for row in rows:
        # Extract the size label (e.g., XS, S, M, etc.)
        size_label = row.css('td.sizeChartTCell span::text').get()

        # Extract measurements for each size
        measurements = row.css('td.sizeChartTCell + td span::text').getall()

        # Store data in the dictionary
        size_chart_data[size_label] = measurements

    # Convert dictionary to JSON
    size_chart_json = json.dumps(size_chart_data, ensure_ascii=False)

    # Print or yield the JSON data
    print(size_chart_json)

with open("details.html", "r") as f:
    content = Selector(text=f.read())
# print(content.css("script#__NEXT_DATA__::text").get())

breadcrumb_div = content.css("div.breadcrumb_wrap")
print("Breadcrumb")
print(extract_breadcrumbs(breadcrumb_div=breadcrumb_div))

image_content_div = content.css("div.pdp_article_image")
print(extract_image_urls(image_div=image_content_div))

chart = content.css("div.sizeChart")
print(chart)
extract_size_chart(size_table=chart)
