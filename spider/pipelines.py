# 此处进行数据处理与数据清洗
import json
import re
import os


class ShortStoryPipeline:
    def process_item(self, item, spider):
        # 获取分类名称，用于创建文件夹
        category = item['category']
        # 定义文件夹路径
        dir_path = os.path.join('..', '..', 'novel', 'shortstory', category)
        os.makedirs(dir_path, exist_ok=True)  # 创建文件夹，如果已存在则忽略

        # 定义文件名：使用item中的title作为文件名，替换掉不能作为文件名的字符
        filename = re.sub(r'[\\/*?:"<>|]', '_', item['title'])
        # 定义文件路径：这里您可以根据需要调整文件存储的路径
        file_path = os.path.join(dir_path, f'{filename}.json')

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 将'content'写入JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            # 如果content是列表形式的，直接将其作为JSON数组写入
            json.dump(item['content'], file, ensure_ascii=False, indent=4)

        return item


class WattpadPipeline:
    def process_item(self, item, spider):
        # 获取分类名称，用于创建文件夹
        category = item['category']
        # 定义文件夹路径
        dir_path = os.path.join('..', '..', 'novel', 'wattpad', category)
        os.makedirs(dir_path, exist_ok=True)  # 创建文件夹，如果已存在则忽略

        # 定义JSON文件的路径
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', item['novel_title'])
        file_path = os.path.join(dir_path, f"{safe_title}.json")

        # 尝试读取现有数据，如果文件不存在或不是有效的JSON，则初始化数据结构
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                # 文件不存在，初始化数据结构
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或不是有效的JSON
            data = {'global_outline': item['global_outline'], 'tags': item['tags'], 'chapters': []}

        # 构建当前章节的信息
        current_chapter = {
            'number': item['chapter_number'],
            'title': item['chapter_title'],
            'content': [item['chapter_content']]
        }

        # 检查章节是否已存在
        chapter_exists = False
        for chapter in data['chapters']:
            if chapter['number'] == item['chapter_number']:
                chapter['content'] += [item['chapter_content']]  # 更新内容
                chapter_exists = True
                break

        if not chapter_exists:
            data['chapters'].append(current_chapter)

        # 按照章节编号排序
        data['chapters'] = sorted(data['chapters'], key=lambda x: x['number'])

        # 将更新后的数据写回JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return item


class RoyalRoadPipeline:
    def process_item(self, item, spider):
        # 获取分类名称，用于创建文件夹
        category = item['category']
        # 定义文件夹路径
        dir_path = os.path.join('..', '..', 'novel', 'royalroad', category)
        os.makedirs(dir_path, exist_ok=True)  # 创建文件夹，如果已存在则忽略

        # 定义JSON文件的路径
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', item['novel_title'])
        file_path = os.path.join(dir_path, f"{safe_title}.json")

        # 尝试读取现有数据，如果文件不存在或不是有效的JSON，则初始化数据结构
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                # 文件不存在，初始化数据结构
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或不是有效的JSON
            data = {'global_outline': item['global_outline'], 'tags': item['tags'], 'chapters': []}

        # 构建当前章节的信息
        current_chapter = {
            'number': item['chapter_index'],
            'title': item['chapter_title'],
            'content': [item['chapter_content']]
        }

        # 检查章节是否已存在
        chapter_exists = False
        for chapter in data['chapters']:
            if chapter['number'] == item['chapter_index']:
                chapter['content'] += [item['chapter_content']]  # 更新内容
                chapter_exists = True
                break

        if not chapter_exists:
            data['chapters'].append(current_chapter)

        # 按照章节编号排序
        data['chapters'] = sorted(data['chapters'], key=lambda x: x['number'])

        # 将更新后的数据写回JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return item


import pymysql
import json


class BiQuGePipeline:
    # def __init__(self):
    #     self.chapters = []

    def open_spider(self, spider):
        # 连接数据库
        self.connection = pymysql.connect(host='localhost', user='lyh', passwd='123', db='novel')
        # 创建一个cursor（可ser）对象执行操作
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        # self.chapters.append(item)
        # return item
        # 插入数据
        content = item['chapter_content']
        deal_content = json.dumps(content, ensure_ascii=False)
        self.cursor.execute(
            "INSERT INTO chapters (novel_id, chapter_number,title,content) VALUES (%s,%s,%s, %s)",
            (item['novel_title'], item['chapter_index'], item['chapter_title'], deal_content))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        # self.chapters.sort(key=lambda x: x['index'])
        # with open('圣墟.json', 'w', encoding='utf-8') as file:
        #     json.dump([dict(chapter) for chapter in self.chapters], file, ensure_ascii=False, indent=4)
        self.cursor.close()
        self.connection.close()


class LiteroticaPipeline:
    def process_item(self, item, spider):
        # 获取分类名称，用于创建文件夹
        category = item['category']
        # 定义文件夹路径
        dir_path = os.path.join('..', '..', 'novel', 'literotica', category)
        os.makedirs(dir_path, exist_ok=True)  # 创建文件夹，如果已存在则忽略

        # 定义文件名：使用item中的title作为文件名，替换掉不能作为文件名的字符
        filename = re.sub(r'[\\/*?:<>|]', '_', item['title'])
        filename = re.sub(r'"', "'", filename)
        # 定义文件路径：这里您可以根据需要调整文件存储的路径
        file_path = os.path.join(dir_path, f'{filename}.json')

        # 尝试读取现有数据，如果文件不存在或不是有效的JSON，则初始化数据结构
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                # 文件不存在，初始化数据结构
                raise FileNotFoundError
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或不是有效的JSON
            data = {'tags': item['tags'], 'content': []}

        # 更新内容
        data['content'].append(item['content'])

        # 将更新后的数据写回JSON文件
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return item

        # # 确保目录存在
        # os.makedirs(os.path.dirname(file_path), exist_ok=True)
        #
        # data = {
        #     'tags': item['tags'],
        #     'content': item['content']
        # }
        #
        # # 将'content'写入JSON文件
        # with open(file_path, 'w', encoding='utf-8') as file:
        #     # 如果content是列表形式的，直接将其作为JSON数组写入
        #     json.dump(data, file, ensure_ascii=False, indent=4)
        #
        # return item
