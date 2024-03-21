import scrapy
from spider.items import LiterOtica
import re
from scrapy.http import Request, Response


class MySpider(scrapy.Spider):
    name = 'literotica'
    start_urls = ['https://www.literotica.com/stories/']

    def parse(self, response):
        categories = response.xpath('//*[@id="up"]/div[3]/div[5]/div[1]/div[1]/div[11]/div/div/a')
        for option in categories:
            cate = option.xpath('./text()').extract_first().lower()
            if cate == 'illustrated' or cate == 'non-english':
                continue
            if cate == 'nonconsent/reluctance':
                cate = 'nonconsent_reluctance'
            url = option.xpath('./@href').extract_first()
            for i in range(1, 3):
                link = url + f'/{i}-page'
                self.logger.info(f'正在抓取 {link}')
                yield response.follow(link, self.parse_novel, meta={'category': cate, 'page': i})
        # yield Request('https://www.literotica.com/s/i-stumbled-into-a-daily-blowjob-ch-04',
        #               callback=self.parse_item, meta={'category': 'ann', 'title': "I STUMBLED INTO A DAILY BLOWJOB CH. 04"})

    def parse_novel(self, response):
        max_page = response.xpath('//*[@id="content"]/div[4]/div/form/select/option/text()').extract()[-1]
        if response.meta['page'] > int(max_page):
            return
        for div in response.xpath('//*[@id="content"]/div[3]/div/h3/a')[:2]:
            # 对每个链接发起跟踪请求
            link = div.xpath('./@href').extract_first()
            novel_title = div.xpath('./text()').extract_first()
            response.meta['title'] = novel_title
            self.logger.info(f'正在抓取{novel_title}')
            yield response.follow(link, self.parse_item, meta=response.meta)

    def parse_item(self, response):
        tags = response.xpath('//*[@id="tabpanel-tags"]/div[2]/a/text()').extract()
        response.meta['tags'] = tags

        para = response.xpath('//*[@id="up"]/div[3]/div[5]/div[1]/div[1]/div[4]/div[1]/div')
        para_number = len(response.xpath('//*[@id="up"]/div[3]/div[5]/div[1]/div[1]/div[4]/div[1]/div/p'))
        # if para_number:
        paragraphs_text = []
        for i in range(1, para_number + 1):
            # 使用string()函数提取每个<p>标签内的文本
            para_text = para.xpath(f'string(./p[{i}])').get()
            # 将提取的文本添加到列表中
            paragraphs_text.append(para_text)

        if paragraphs_text:
            self.logger.info(f'{response.url}有数据')
            item = LiterOtica()
            # 获取小说内容
            item['category'] = response.meta['category']
            item['title'] = response.meta['title']
            item['tags'] = response.meta['tags']
            item['content'] = paragraphs_text
            yield item
            # 检查是否有下一页
            max_page = response.xpath('//*[@id="up"]/div[3]/div[5]/div[1]/div[2]/div/div/a/text()').extract()
            if max_page:
                if re.search(r'(page=\d+)', response.url):
                    if int(response.url.split('=')[-1]) >= int(max_page[-1]):
                        return
                    next_page_number = int(response.url.split('=')[-1]) + 1
                    next_page_url = response.url.rsplit('=', 1)[0] + f'={next_page_number}'
                else:
                    next_page_url = f'{response.url}?page=2'
                # 发起对下一页的请求
                yield response.follow(next_page_url, callback=self.parse_item, meta=response.meta)
        else:
            # 如果页面没有内容，则停止
            self.logger.info(f'{response.url}无数据')
