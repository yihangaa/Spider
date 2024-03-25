import scrapy
from spider.items import RoyalRoad
# 我删除了这行注释

class MySpider(scrapy.Spider):
    name = 'nifty'
    start_urls = ['https://www.nifty.org/nifty/']
#
    def parse(self, response):
        categories = response.xpath('//*[@id="myNavbar"]/ul[1]/li[1]/ul/li/a')
        for li in categories[:4]:
            cate = li.xpath('./text()').extract_first().lower()
            url = li.xpath('./@href').extract_first()
            self.logger.info(f'正在抓取第一层 {cate} url: {url}')
            yield response.follow(url, self.parse_classes, meta={'category': cate})
        # yield Request('https://www.nifty.org/nifty/bisexual/adult-friends/',
        #               callback=self.parse_novel, meta={'category': 'bisexual', 'tags': 'adult-friends'})

    def parse_classes(self, response):
        classes = response.xpath('/html/body/div/div/div[2]/ul/li/a')
        for li in classes:
            tag = li.xpath('./text()').extract_first()
            url = li.xpath('./@href').extract_first()
            response.meta['tags'] = tag
            self.logger.info(f'正在抓取第二层 {tag} url: {url}')
            yield response.follow(url, self.parse_novel, meta=response.meta)

    def parse_novel(self, response):
        if response.meta['category'] == 'gay':
            novels = response.xpath('//*[@id="scroll"]/div')
            for div in novels[1:]:
                novel_title = div.xpath('./div[3]/a/text()').extract_first()
                url = div.xpath('./div[3]/a/@href').extract_first()
                response.meta['novel_title'] = novel_title

                if div.xpath('./div[1]/text()').extract_first() == 'Dir':
                    self.logger.info(f'正在抓取小说 {novel_title} url: {url},识别为Dir')
                    yield response.follow(url, self.parse_chapter, meta=response.meta)
                else:
                    self.logger.info(f'正在抓取小说 {novel_title} url: {url},识别为单章')
                    response.meta['chapter_title'] = 'None'
                    response.meta['chapter_index'] = 1
                    yield response.follow(url, self.parse_item, meta=response.meta)
        else:
            novels = response.xpath('/html/body/div/div/div[2]/div[2]/table//tr')
            for div in novels[1:]:
                novel_title = div.xpath('./td[3]/a/text()').extract_first()
                url = div.xpath('./td[3]/a/@href').extract_first()
                response.meta['novel_title'] = novel_title
                # self.logger.info(f'正在抓取小说 {novel_title} url: {url}')
                if div.xpath('./td[1]/text()').extract_first() == 'Dir':
                    self.logger.info(f'正在抓取小说 {novel_title} url: {url},识别为Dir')
                    yield response.follow(url, self.parse_chapter, meta=response.meta)
                else:
                    self.logger.info(f'正在抓取小说 {novel_title} url: {url},识别为单章')
                    response.meta['chapter_title'] = 'None'
                    response.meta['chapter_index'] = 1
                    yield response.follow(url, self.parse_item, meta=response.meta)

    def parse_chapter(self, response):
        chapters = response.xpath('/html/body/div/div/div[2]/div[2]/table//tr/td[3]/a')
        for index, tr in enumerate(chapters):
            # 对每个链接发起跟踪请求
            link = tr.xpath('./@href').extract_first()
            chapter_title = tr.xpath('./text()').extract_first()
            self.logger.info(f'正在抓取{chapter_title},url: {link}')
            response.meta['chapter_index'] = index + 1
            response.meta['chapter_title'] = chapter_title
            yield response.follow(link, self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = RoyalRoad()
        # 获取小说内容
        item['category'] = response.meta['category']
        item['tags'] = response.meta['tags']
        item['novel_title'] = response.meta['novel_title']
        item['chapter_title'] = response.meta['chapter_title']
        item['chapter_content'] = response.body.decode('utf-8', errors='ignore')
        item['chapter_index'] = response.meta['chapter_index']
        yield item
