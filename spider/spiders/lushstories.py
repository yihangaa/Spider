import scrapy
from spider.items import RoyalRoad
from scrapy.http import Request, Response
import re


class MySpider(scrapy.Spider):
    name = 'lushstories'
    start_urls = ['https://www.lushstories.com/stories/anal?genre=anal']

    def parse(self, response):
        categories = response.xpath('//*[@id="__layout"]/div/div[2]/div[1]/div/div/div[1]/div[3]/div/div[2]/ul[2]/li/a')
        for li in categories[:-1]:
            cate = li.xpath('./text()').extract_first().strip().lower().replace(" ", "-")
            # print(cate)
            # for i in range(1, 101):
            #     # link = f'https://www.lushstories.com/stories/{cate}?genre={cate}&page={i}'
            #     self.logger.info(f'正在抓取 {link}')
            #     yield response.follow(link, self.parse_novel, meta={'category': cate})
            link = f'https://www.lushstories.com/stories/{cate}'
            self.logger.info(f'正在抓取 {cate}')
            yield response.follow(link, self.parse_page, meta={'category': cate})
            # yield Request('https://www.lushstories.com/stories/anal/polo-ponies',
            #               callback=self.parse_chapter,
            #               meta={'category': 'anal', 'novel_title': "Polo Ponies", "novel_tags": ["anal", "pun"]})

    def parse_page(self, response):
        # 获取总页数，这个XPath需要根据实际页面结构调整
        total_pages = response.xpath(
            '//*[@id="__layout"]/div/div[2]/div[1]/div/div/nav/span/span/text()').extract_first()
        total_pages = re.search(r'\d+', total_pages).group()
        if total_pages:
            total_pages = int(total_pages)
            # for i in range(1, total_pages+1):
            for i in range(1, 3):
                link = f'https://www.lushstories.com/stories/{response.meta["category"]}?genre={response.meta["category"]}&page={i}'
                self.logger.info(f'正在抓取 {link}')
                yield response.follow(link, self.parse_novel, meta=response.meta, dont_filter=True)
            # current_page = response.meta.get('page', 1)
            # if current_page < total_pages:
            #     next_page = current_page + 1
            #     next_page_link = f'https://www.lushstories.com/stories/{response.meta["category"]}?genre={response.meta["category"]}&page={next_page}'
            #     yield response.follow(next_page_link, self.parse_novel,
            #                           meta={'category': response.meta['category'], 'page': next_page})

    def parse_novel(self, response):
        for div in response.xpath('//*[@id="__layout"]/div/div[2]/div[1]/div/div/div/article')[:2]:
            # 对每个链接发起跟踪请求
            link = div.xpath('./div/div/div/h2/a/@href').extract_first()
            novel_title = div.xpath('./div/div/div/h2/a/text()').extract_first().strip()
            novel_tags = div.xpath('./footer//a/text()').extract()
            novel_tags = [item.strip() for item in novel_tags]
            response.meta['novel_title'] = novel_title
            response.meta['novel_tags'] = novel_tags
            self.logger.info(f'正在抓取{novel_title},tags为{novel_tags}')
            yield response.follow(link, self.parse_chapter, meta=response.meta)

    def parse_chapter(self, response):
        if response.xpath('//*[@id="__layout"]/div/div[2]/div/div/div/div[2]//div/div[2]/ol/li/a'):
            for index, tr in enumerate(
                    response.xpath('//*[@id="__layout"]/div/div[2]/div/div/div/div[2]//div/div[2]/ol/li/a')):
                link = tr.xpath('./@href').extract_first().strip()
                chapter_title = tr.xpath('./text()').extract_first().strip()
                # print(chapter_title, link)
                self.logger.info(f'正在抓取{chapter_title},url: {link}')
                response.meta['chapter_title'] = chapter_title
                response.meta['chapter_index'] = index + 1
                yield response.follow(link, self.parse_item, meta=response.meta, dont_filter=True)
        else:
            response.meta['chapter_title'] = 'None'
            response.meta['chapter_index'] = 1
            yield response.follow(response.url, self.parse_item, meta=response.meta, dont_filter=True)

    def parse_item(self, response):
        item = RoyalRoad()
        # 获取小说内容
        item['category'] = response.meta['category']
        item['novel_title'] = response.meta['novel_title']
        # item['global_outline'] = response.meta['global_outline']
        item['tags'] = response.meta['novel_tags']
        item['chapter_title'] = response.meta['chapter_title']
        # item['chapter_content'] = paragraphs_text
        item['chapter_content'] = response.xpath(
            '//*[@id="__layout"]/div/div[2]/div/div/div/div[4]/div[1]/div/div/p/text()').extract()

        item['chapter_index'] = response.meta['chapter_index']
        yield item
