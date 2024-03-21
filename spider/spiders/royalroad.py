import scrapy
from spider.items import RoyalRoad


class MySpider(scrapy.Spider):
    name = 'royalroad'
    start_urls = ['https://www.royalroad.com/fictions/best-rated?genre=']

    def parse(self, response):
        categories = response.xpath('//*[@id="genre"]/option')
        for option in categories[1:]:
            cate = option.xpath('./text()').extract_first().lower()
            if cate == 'short story':
                cate = 'one_shot'
            if cate == 'sci-fi':
                cate = 'sci_fi'
            for i in range(6, 101):
                link = f'https://www.royalroad.com/fictions/best-rated?page={i}&genre={cate}'
                self.logger.info(f'正在抓取{link}')
                yield response.follow(link, self.parse_novel, meta={'category': cate})

    def parse_novel(self, response):
        for div in response.xpath('//*[@id="result"]/div'):
            # 对每个链接发起跟踪请求
            link = div.xpath('./div/h2/a/@href').extract_first()
            novel_title = div.xpath('./div/h2/a/text()').extract_first()
            novel_tags = div.xpath('./div/div[1]/span[2]/a/text()').extract()
            response.meta['novel_title'] = novel_title
            response.meta['novel_tags'] = novel_tags
            self.logger.info(f'正在抓取{novel_title},tags为{novel_tags}')
            yield response.follow(link, self.parse_chapter, meta=response.meta)

    def parse_chapter(self, response):
        # 获取章节链接
        para = response.xpath('//div[@class="description"]/div')
        paragraphs_text = []
        for i in range(1, len(response.xpath('//div[@class="description"]/div/p')) + 1):
            # 使用string()函数提取每个<p>标签内的文本
            para_text = para.xpath(f'string(./p[{i}])').get()
            # 将提取的文本添加到列表中
            paragraphs_text.append(para_text)
        response.meta['global_outline'] = paragraphs_text
        # print(paragraphs_text)
        for index, tr in enumerate(response.xpath('//*[@id="chapters"]/tbody/tr/td[1]/a')):
            link = tr.xpath('./@href').extract_first().strip()
            chapter_title = tr.xpath('./text()').extract_first().strip()
            # print(chapter_title, link)
            self.logger.info(f'正在抓取{chapter_title}')
            response.meta['chapter_title'] = chapter_title
            response.meta['chapter_index'] = index + 1
            yield response.follow(link, self.parse_item, meta=response.meta)

    def parse_item(self, response):
        para = response.xpath('//div[@class="chapter-inner chapter-content"]')
        para_number = len(response.xpath('//div[@class="chapter-inner chapter-content"]/p'))
        if para_number:
            paragraphs_text = []
            for i in range(1, para_number + 1):
                # 使用string()函数提取每个<p>标签内的文本
                para_text = para.xpath(f'string(./p[{i}])').get()
                # 将提取的文本添加到列表中
                paragraphs_text.append(para_text)
        else:
            para_number = len(response.xpath('//div[@class="chapter-inner chapter-content"]/div'))
            paragraphs_text = []
            for i in range(1, para_number + 1):
                # 使用string()函数提取每个<p>标签内的文本
                para_text = para.xpath(f'string(./div[{i}])').get()
                # 将提取的文本添加到列表中
                paragraphs_text.append(para_text)

        item = RoyalRoad()
        # 获取小说内容
        item['category'] = response.meta['category']
        item['novel_title'] = response.meta['novel_title']
        item['global_outline'] = response.meta['global_outline']
        item['tags'] = response.meta['novel_tags']
        item['chapter_title'] = response.meta['chapter_title']
        item['chapter_content'] = paragraphs_text
        item['chapter_index'] = response.meta['chapter_index']
        yield item
