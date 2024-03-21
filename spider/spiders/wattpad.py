import scrapy
import re
from scrapy.http import Request, Response
from ..items import WattpadItem
import json


class WattpadSpider(scrapy.Spider):
    name = "wattpad"
    # allowed_domains = ["www.wattpad.com"]
    # start_urls = ["https://www.wattpad.com/stories/adventure"]
    start_urls = ["https://www.wattpad.com/v5/hotlist?tags=fanfiction&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=fantasy&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=historicalfiction&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=horror&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=humor&language=1&limit=100&fields=stories"
                  "https://www.wattpad.com/v5/hotlist?tags=lgbt&language=1&limit=100&fields=stories"
                  "https://www.wattpad.com/v5/hotlist?tags=mystery&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=newadult&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=nonfiction&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=paranormal&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=poetry&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=romance&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=sciencefiction&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=shortstory&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=teenfiction&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=thriller&language=1&limit=100&fields=stories",
                  "https://www.wattpad.com/v5/hotlist?tags=werewolf&language=1&limit=100&fields=stories"]

    def parse(self, response):
        str_data = response.body.decode('utf-8')

        # 然后，使用json.loads()将字符串转换为Python字典
        json_data = json.loads(str_data)
        cate = re.search('tags=([^&]+)', response.url).group(1)

        for story in json_data["stories"]:
            title = story["title"],
            description = story.get("description", "no description")
            tags = story["tags"],
            url = story["url"]
            yield response.follow(url, self.parse_outline_chapter,
                                  meta={'novel_title': title[0], 'global_outline': description, 'tags': tags[0],
                                        'category': cate})
        # print(parsed_data)

        # print(json_data['stories'])
        # 剔除前三个无关分类
        # for li in response.xpath('//*[@id="discover-dropdown"]/div[2]/div[1]/ul/li/a')[5:7]:
        #     link = li.xpath('./@href').extract_first()
        #     category = li.xpath('./text()').extract_first()
        #     self.logger.info(f'开始爬取{category}，link：{link}')
        #     yield response.follow(link, self.parse_get_novel, meta={'category': category})
        # yield Request('https://www.wattpad.com/1710912-delta-a-spy-novel-chapter-one',
        #               callback=self.parse_get_content)

    # def parse_get_novel(self, response):
    #     print(response.url, response.meta['title'])
    #     for div in response.xpath('//*[@id="browse-results-item-view"]/div/div/div/div/a[1]'):
    #         link = div.xpath('./@href').extract_first()
    #         novel_title = div.xpath('./text()').extract_first()
    #         response.meta['novel_title'] = novel_title
    #         self.logger.info(f'开始爬取{novel_title}，类别为{response.meta["category"]}，link：{link}')
    #         # yield response.follow(link, self.parse_outline_chapter, meta=response.meta)

    def parse_outline_chapter(self, response):
        # global_outline = response.xpath(
        #     '/html/body/div[4]/div/div/div/div[2]/div[1]/div[2]/div/pre/text()').extract_first()

        # response.meta['global_outline'] = global_outline

        chapters = response.xpath('/html/body/div[4]/div/div/div/div[2]/div[1]/div[5]/div[2]/ul/li')
        # total_chapters = len(chapters)

        for index, li in enumerate(chapters):
            chapter_links = li.xpath('./a/@href').extract_first()
            chapter_title = li.xpath('./a/div/div/div[2]/text()').extract_first()
            is_pay = li.xpath('./a/div[2]/svg/title/text()').extract_first()
            if is_pay:
                self.logger.info(f'{response.meta["novel_title"]}为付费书籍，无法访问')
                return
            # 列表中第一个chapter获得最高优先级
            # chapter_number = total_chapters - index
            response.meta['chapter_title'] = chapter_title
            response.meta['chapter_number'] = index + 1
            self.logger.info(
                # f'正在爬取{response.meta["novel_title"]}的章节{chapter_title}，link：{chapter_links}，类别为{response.meta["category"]}')
                f'正在爬取{response.meta["novel_title"]}的章节{chapter_title}，link：{chapter_links}')
            yield response.follow(chapter_links, callback=self.parse_get_content, meta=response.meta)

    def parse_get_content(self, response):
        para = response.xpath('/html/body/div[4]/div/main/article/div[3]/div/div[2]/div[1]/pre')
        # 初始化一个空列表来存储所有段落的文本
        paragraphs_text = []
        for i in range(1, len(response.xpath('/html/body/div[4]/div/main/article/div[3]/div/div[2]/div[1]/pre/p')) + 1):
            # 使用string()函数提取每个<p>标签内的文本
            para_text = para.xpath(f'string(./p[{i}])').get()
            # 将提取的文本添加到列表中
            paragraphs_text.append(para_text)

        if paragraphs_text:
            # item保存数据
            self.logger.info(f'{response.url}有数据')
            item = WattpadItem()
            item['category'] = response.meta['category']
            item['novel_title'] = response.meta['novel_title']
            item['global_outline'] = response.meta['global_outline']
            item['tags'] = response.meta['tags']
            item['chapter_title'] = response.meta['chapter_title']
            item['chapter_content'] = paragraphs_text
            item['chapter_number'] = response.meta['chapter_number']
            yield item
            # 检查是否有下一页
            if re.search(r'(/page/\d+)', response.url):
                next_page_number = int(response.url.split('/')[-1]) + 1
                next_page_url = response.url.rsplit('/', 1)[0] + f'/{next_page_number}'
            else:
                next_page_url = f'{response.url}/page/2'
            # 发起对下一页的请求
            yield response.follow(next_page_url, callback=self.parse_get_content, meta=response.meta)
        else:
            # 如果页面没有内容，则停止
            self.logger.info(f'{response.url}无数据')
