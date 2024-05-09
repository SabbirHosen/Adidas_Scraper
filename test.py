from scrapy import Selector

with open("details.html", "r") as f:
    content = Selector(text=f.read())
print(content.css("script#__NEXT_DATA__::text").get())
breadcrumb_category = content.css(".breadcrumb_category::text").get()