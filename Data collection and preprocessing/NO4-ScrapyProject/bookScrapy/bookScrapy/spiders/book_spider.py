from scrapy import Spider


# 创建爬虫类，必须继承SPider类
class BookSpider(Spider):
    # 给爬虫起一个唯一的名字
    name = 'book'
    # 设置爬取的网站地址
    start_urls = ['https://books.toscrape.com/']
    # 重写解析方法
    def parse(self, response):
        # 解析数据
        name = response.xpath('//*[@id="default"]/div/div/div/div/section/div[2]/ol/li[1]/article/h3/a/text()')[0]
        print(name + '============================')