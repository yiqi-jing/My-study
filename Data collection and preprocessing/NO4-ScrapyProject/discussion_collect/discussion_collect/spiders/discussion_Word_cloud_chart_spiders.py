""" 
此子项目用于实现词云图的设计，词云图设计是一种数据可视化的技术，使用python 而非findebi工具。
对清洗后的详细页内容中的用户评论进行词云的生成，跳出每个文章中的热点词汇，帮助作者了解大众的方向，
以便后续发布的内容进行优化和改进。
"""
from scrapy import Spider

class DiscussionSpider(Spider):
    name = 'discussion_Word_cloud_chart_spiders'