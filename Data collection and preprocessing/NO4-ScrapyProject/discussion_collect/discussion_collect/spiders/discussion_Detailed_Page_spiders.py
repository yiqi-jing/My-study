""" 
此子项目用于爬取作者标题的详细页内容的文本内容和评论内容，并保存为json格式文件，
后续对JSON文件进行数据处理，过滤所有的特殊符号，只保留纯文本内容和数字以及常用标点符号，
清洗后保存为新的CSV文件，
文件命名格式为：discussion_Detailed_Page_cleaned.csv,
标头为：标题，清洗后的正文内容，清洗后的评论内容列表（多个评论以分隔符分隔），评论带上评论人的用户名。
 """
from scrapy import Spider

class DiscussionSpider(Spider):
    name = 'discussion_Detailed_Page_spiders'