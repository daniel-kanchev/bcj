import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bcj.items import Article


class BcjSpider(scrapy.Spider):
    name = 'bcj'
    start_urls = ['https://www.bcj.ch/fr/La-Banque/Actualites.html']

    def parse(self, response):
        articles = response.xpath('//div[@class="col-md-3"]')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            if link:
                date = article.xpath('.//span/text()').get()
                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        if date:
            date = date.strip()

        content = response.xpath('//div[@class="part BlocText"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
