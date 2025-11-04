# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscrapyPipeline:
    def process_item(self, item, spider):
        # 把item对象持久化到文件中
        with open('books.txt', 'a', encoding='utf-8') as f:
            f.write(f"===== 第 {spider.book_count - 1} 本书 =====\n")
            f.write(f"书名: {item['name']}\n")
            f.write(f"星级: {item['star']}\n")
            f.write(f"价格: {item['price']}\n")
            f.write(f"封面图片: {item['pic_url']}\n")
            f.write(f"详情页: {item['detail_url']}\n")

        return item
