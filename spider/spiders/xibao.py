import scrapy
from ..items import biquge


class XibaoSpider(scrapy.Spider):
    name = "xibao"
    start_urls = ["https://www.bq7.cc/top/"]

    def parse(self, response):
        for a in response.xpath('//div[@class="wrap rank"]//li/a'):
            novel_title = a.xpath('./text()').extract_first()
            link = a.xpath('./@href').extract_first()
            self.logger.info(f'正在抓取{novel_title}，{link}')
            yield response.follow(link, callback=self.parse_novel, meta={"novel_title": novel_title})

    def parse_novel(self, response):
        # print('进来了')
        for index, a in enumerate(response.xpath('//div[@class="listmain"]//dd/a')):
            if index == 10:
                continue

            chapter_title = a.xpath('./text()').extract_first()
            link = a.xpath('./@href').extract_first()
            response.meta['chapter_index'] = index
            response.meta['chapter_title'] = chapter_title
            # print(title, link)
            self.logger.info(f'{chapter_title},{link}')
            yield response.follow(link, callback=self.parse_content, meta=response.meta)

    def parse_content(self, response):
        item = biquge()
        item['novel_title'] = response.meta['novel_title']
        item['chapter_index'] = response.meta['chapter_index']
        item['chapter_title'] = response.meta['chapter_title']

        content = response.xpath('//*[@id="chaptercontent"]/text()').extract()
        deal_content = [i.replace('\xa0', '') for i in content]
        item['chapter_content'] = deal_content
        self.logger.info(f'正在爬取{item["chapter_title"]}')
        yield item
