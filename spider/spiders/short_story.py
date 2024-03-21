import scrapy
from scrapy import Request
from ..items import ShortstoryItem
import logging


class MyspiderSpider(scrapy.Spider):
    name = "shortstory"
    start_urls = ["https://www.short-story.me/stories"]

    def parse(self, response):
        self.logger.info('开始爬取分类页面: %s', response.url)
        for div in response.xpath('/html/body/div/div[4]/div/main/div[2]/div/div/div[2]/div'):
            category = div.xpath('./h3/a/text()').extract_first().replace('\n', '').replace('\t', '')
            link = div.xpath('./h3/a/@href').extract_first()
            novel_count = div.xpath('./h3/span/text()').extract_first().replace('\n', '').replace('\t', '')
            page_num = int(int(novel_count) / 100)
            for i in range(page_num + 1):
                deal_link = link + f'?start={i * 100}'
                # print(category, deal_link)
                self.logger.info('处理分类: %s，链接: %s', category, deal_link)
                yield response.follow(deal_link, callback=self.parse_novel,
                                      meta={'category': category})

    def parse_novel(self, response):
        for a in response.xpath('//*[@id="adminForm"]/table/tbody/tr/td/a'):
            title = a.xpath('./text()').extract_first().replace('\n', '').replace('\t', '')
            link = a.xpath('./@href').extract_first()
            response.meta['title'] = title
            # print(title, link)
            self.logger.info('爬取小说页面: %s，标题: %s', link, title)
            yield response.follow(link, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = ShortstoryItem()
        item['category'] = response.meta['category']
        item['title'] = response.meta['title']
        # 内容
        para = response.xpath('//*[@itemprop="articleBody"]')
        # 初始化一个空列表来存储所有段落的文本
        paragraphs_text = []
        for i in range(1, len(response.xpath('//*[@itemprop="articleBody"]/p')) + 1):
            # 使用string()函数提取每个<p>标签内的文本
            para_text = para.xpath(f'string(./p[{i}])').get().replace('\xa0', ' ').strip()
            # 将提取的文本添加到列表中
            paragraphs_text.append(para_text)
        item['content'] = paragraphs_text
        self.logger.info(f'爬虫结束，成功提取并发送小说: {item["title"]}')
        yield item
