from scrapy import Spider

class BookSpider(Spider):
    name = 'book'
    start_urls = ['https://books.toscrape.com/']
    
    def parse(self, response):
        # 定位所有书籍节点
        books = response.xpath('//*[@id="default"]/div/div/div/div/section/div[2]/ol/li')
        
        # 初始化计数器（从1开始计数）
        book_count = 1
        
        # 遍历每本书，提取信息并计数
        for book in books:
            # 打印当前是第几本书
            print(f"===== 第 {book_count} 本书 =====")
            
            # 书名
            name = book.xpath('article/h3/a/text()').get()
            
            # 星级
            star = book.xpath('article/p[contains(@class, "star-rating")]/@class').get()
            star = star.split()[-1] if star else '未知'
            
            # 价格（新增）
            price = book.xpath('article/div[2]/p[@class="price_color"]/text()').get()
            price = price.strip() if price else '未知'  # 去除可能的空格
            
            # 封面图片网址
            pic_url = book.xpath('article/div[1]/a/img/@src').get()
            pic_url = response.urljoin(pic_url) if pic_url else '未知'
            
            # 书籍详情页网址
            detail_url = book.xpath('article/h3/a/@href').get()
            detail_url = response.urljoin(detail_url) if detail_url else '未知'
            
            # 打印书籍信息
            print(f"书名：{name}")
            print(f"星级：{star}")
            print(f"价格：{price}")  # 新增价格打印
            print(f"封面图片：{pic_url}")
            print(f"详情页：{detail_url}")
            print("==" * 50)
            
            # 计数器自增（下一本书）
            book_count += 1