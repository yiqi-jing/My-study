# Scrapy settings for discussion_collect project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "discussion_collect"

SPIDER_MODULES = ["discussion_collect.spiders"]
NEWSPIDER_MODULE = "discussion_collect.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "discussion_collect (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "discussion_collect.middlewares.DiscussionCollectSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "discussion_collect.middlewares.DiscussionCollectDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "discussion_collect.pipelines.DiscussionCollectPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# User-Agent设置为常见浏览器，避免被轻易识别为爬虫
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

# 并发与延迟（核心反爬，使用随机范围替代固定值）
CONCURRENT_REQUESTS = 8  # 合理控制总并发（避免过高触发反爬）
CONCURRENT_REQUESTS_PER_DOMAIN = 4  # 单域名并发更保守
CONCURRENT_REQUESTS_PER_IP = 2  # 新增：按IP限制并发（比按域名更严格）
DOWNLOAD_DELAY = 1.0  # 基础延迟
RANDOMIZE_DOWNLOAD_DELAY = True  # 新增：开启随机延迟（实际延迟为0.5*DOWNLOAD_DELAY ~ 1.5*DOWNLOAD_DELAY）
DOWNLOAD_TIMEOUT = 20  # 超时时间

# 日志配置
LOG_LEVEL = 'WARNING'  # 只输出警告及以上日志
LOG_FILE = 'scrapy_logs.log'  # 日志写入文件，避免控制台输出暴露
LOG_STDOUT = False  # 禁止将日志输出到标准输出

# SSL与请求安全，跳跃不必要的验证
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SSL_VERIFY = False  # 禁用SSL证书验证
ROBOTSTXT_OBEY = False  # 不遵守robots.txt规则
TELNETCONSOLE_ENABLED = False  # 禁用Telnet控制台

# 1. 重试策略
RETRY_TIMES = 2  # 重试次数
RETRY_HTTP_CODES = [408, 500, 502, 503, 504, 429]  # 新增429（请求过于频繁）
RETRY_PRIORITY_ADJUST = -1  # 重试请求优先级降低，避免集中重试

# Cookies处理
COOKIES_ENABLED = True
COOKIES_DEBUG = False  # 禁用Cookies调试日志
DEFAULT_REQUEST_HEADERS = {  # 新增：完善请求头，模拟真实浏览器
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# 限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1  # 初始延迟
AUTOTHROTTLE_MAX_DELAY = 10  # 最大延迟
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # 目标并发数
AUTOTHROTTLE_DEBUG = False  # 禁用自动限速调试

# 指纹识别隐藏Scrapy爬虫
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
DEFAULT_REQUEST_HEADERS.pop('User-Agent', None)  # 配合随机User-Agent中间件

# 下载中间件
DOWNLOADER_MIDDLEWARES = {
    # 随机User-Agent中间件（需安装：pip install scrapy-user-agents）
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    
    # 禁用默认的重试中间件
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    
    # 启用压缩中间件
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
}

# 伪装爬虫中间件
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
}

# 备用多维反爬配置
DEPTH_LIMIT = 5  # 限制爬取深度，避免爬取过深触发反爬
DEPTH_PRIORITY = 1  # 深度优先爬取，模拟用户浏览行为
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'  # FIFO队列，模拟用户访问顺序
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'  # 内存统计，避免写入文件暴露