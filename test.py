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


def extract_size_chart(response):
    # Extracting measurement types from the first table
    measurement_types = response.css(
        '.sizeChartTable:first-child .sizeChartTRow:nth-child(n+2) .sizeChartTHeaderCell::text').extract()
    print("measurement_types", measurement_types)

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
    print("row_data", row_data)
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
    json_data = json.dumps(combined_data, indent=4, ensure_ascii=False)
    print(json_data)

    # filename = 'shirt_sizes.json'
    # with open(filename, 'w') as f:
    #     json.dump(combined_data, f, indent=4)
    #
    # print(f'Saved file {filename}')


# def extract_size_chart(size_table):
#     rows = size_table.css('div.sizeChart table.sizeChartTable tbody tr')
#
#     # Initialize dictionary to store size chart data
#     size_chart_data = {}
#
#     # Iterate over rows
#     for row in rows:
#         # Extract the size label (e.g., XS, S, M, etc.)
#         size_label = row.css('td.sizeChartTCell span::text').get()
#
#         # Extract measurements for each size
#         measurements = row.css('td.sizeChartTCell + td span::text').getall()
#
#         # Store data in the dictionary
#         size_chart_data[size_label] = measurements
#
#     # Convert dictionary to JSON
#     size_chart_json = json.dumps(size_chart_data, ensure_ascii=False)
#
#     # Print or yield the JSON data
#     print(size_chart_json)

def extract_reviews(content):
    review_elements = content.css("div.BVRRContentReview")
    print(review_elements)

    for review_element in review_elements:
        # Extract review date
        review_date = review_element.css("div.BVRRReviewDateContainer *::text").getall()

        # Extract review rating
        review_rating = review_element.xpath('.//span[@class="BVRRNumber BVRRRatingNumber"]/text()').get()

        # Extract review title
        review_title = review_element.xpath('.//span[@class="BVRRValue BVRRReviewTitle"]/text()').get()

        # Extract review description
        review_description = review_element.xpath('.//div[@class="BVRRReviewText"]/descendant::*/text()').getall()
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
        print(data)


def extract_rating(response):
    review_rating_dict = {}
    review_ratings = response.css("div.BVRRSecondaryRatingsContainer div.BVRRRatingEntry")
    for review_rating in review_ratings:
        title = review_rating.css("div.BVRRRatingHeader ::text").get().strip()
        rating = review_rating.css("div.BVRRRatingRadioImage img::attr(title)").get()
        review_rating_dict[title] = rating

    return review_rating_dict


with open("detailsIS1540.html", "r") as f:
    content = Selector(text=f.read())
# print(content.css("script#__NEXT_DATA__::text").get())

breadcrumb_div = content.css("div.breadcrumb_wrap")
print("Breadcrumb")
print(extract_breadcrumbs(breadcrumb_div=breadcrumb_div))

image_content_div = content.css("div.pdp_article_image")
print(extract_image_urls(image_div=image_content_div))

extract_size_chart(response=content)

category = " ".join(content.css("a.groupName span::text").getall())
print("category", category)
title = content.css("div.articleInformation h1.itemTitle::text").get()
print("title", title)
price = content.css("div.articlePrice ::text").get()
print("price", price)
available_size = content.css("ul.sizeSelectorList li button::text").getall()
print("available_size", available_size)

description_title = content.css("div.js-componentsTabTarget h4::text").get()
print("description_title", description_title)
general_description = content.css("div.inner div.description_part *::text").getall()
general_description = " ".join(general_description)
print("general_description", general_description)
item_description = content.css("div.inner ul.articleFeatures *::text").getall()
item_description = " ".join(item_description)

print("item_description", item_description)

kws = content.css("div.itemTagsPosition *::text").getall()
kws = ", ".join(kws)
print("kws", kws)
print(extract_rating(response=content))

rating = content.css("div.BVRRQuickTakeCustomWrapper div.BVRRRatingNormalOutOf  span.BVRRNumber.BVRRRatingNumber::text").get()
print("rating", rating)

number_of_review = content.css("div.BVRRQuickTakeCustomWrapper span.BVRRValue span.BVRRBuyAgainTotal::text").get()
print("number_of_review", number_of_review)

recommendation_percentage = content.css("div.BVRRQuickTakeCustomWrapper .BVRRBuyAgainPercentage span::text").get()
print("recommendation_percentage", recommendation_percentage)

cordinate_item_div = content.css("div.coordinate_inner div.coordinate_item_container")
print("product link", cordinate_item_div.css("div.detail a::attr(href)").get())
print("image link", cordinate_item_div.css("div.detail img::attr(src)").get())
print("product title", cordinate_item_div.css("div.detail span.titleWrapper ::text").get())
print("product price", cordinate_item_div.css("div.detail div.mdl-price ::text").get())
print(content.css("div.coordinate_inner div.coordinate_item_container"))