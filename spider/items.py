import scrapy


class ShortstoryItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    chapter = scrapy.Field()  # 新增字段
    pass


class WattpadItem(scrapy.Item):
    category = scrapy.Field()
    novel_title = scrapy.Field()
    global_outline = scrapy.Field()
    tags = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_content = scrapy.Field()
    chapter_number = scrapy.Field()
    pass


class RoyalRoad(scrapy.Item):
    category = scrapy.Field()
    novel_title = scrapy.Field()
    global_outline = scrapy.Field()
    tags = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_content = scrapy.Field()
    chapter_index = scrapy.Field()
    pass


class LiterOtica(scrapy.Item):
    category = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    pass


class biquge(scrapy.Item):
    novel_title = scrapy.Field()
    chapter_index = scrapy.Field()
    chapter_title = scrapy.Field()
    chapter_content = scrapy.Field()
    pass
