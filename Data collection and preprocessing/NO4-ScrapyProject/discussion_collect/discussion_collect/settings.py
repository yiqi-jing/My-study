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


# 禁用SSL警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' # 模拟常见浏览器的User-Agent
DOWNLOAD_DELAY = 1.0  # 随机值可在爬虫中动态设置
CONCURRENT_REQUESTS = 2 # 限制总并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 2 # 限制每个域名的并发请求数
DOWNLOAD_TIMEOUT = 15 # 设置下载超时时间
LOG_LEVEL = 'INFO' # 设置日志级别
TELNETCONSOLE_ENABLED = False # 禁用Telnet控制台
ROBOTSTXT_OBEY = False  # 不遵守robots.txt规则
SSL_VERIFY = False # 禁用SSL证书验证
AUTOTHROTTLE_ENABLED = True # 启用自动限速
AUTOTHROTTLE_START_DELAY = 1 # 初始下载延迟
AUTOTHROTTLE_MAX_DELAY = 5  # 最大下载延迟
COOKIES_ENABLED = True # 启用Cookies
RETRY_TIMES = 3 # 设置重试次数
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504] # 设置需要重试的HTTP状态码

CONCURRENT_REQUESTS = 12 # 增加总并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 6 # 增加每个域名的并发请求数
DOWNLOAD_DELAY = 0.5  # 增加延迟避免反爬
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' # 更新User-Agent
LOG_LEVEL = 'WARNING' # 调整日志级别
DOWNLOAD_TIMEOUT = 20 # 增加下载超时时间
RETRY_TIMES = 2 # 减少重试次数
RETRY_HTTP_CODES = [408, 500, 502, 503, 504] # 更新需要重试的HTTP状态码

# 启用代理中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'discussion_collect.middlewares.ProxyMiddleware': 760,
}

# 代理列表
PROXY_LIST = [
    'http://123.456.789.000:8080',
    'http://234.567.890.123:3128',
    'http://345.678.901.234:80'
]
# 代理切换策略
PROXY_MODE = 0  # 0: 随机选择代理，1: 顺序选择代理
# 服务器肉鸡
TARGET_SERVERS = [
    'http://targetserver1.com',
    'http://targetserver2.com'
]
#虚拟海外IP设置
DOWNLOADER_MIDDLEWARES.update({
    'discussion_collect.middlewares.OverseasIPMiddleware': 770,
})

# 海外IP服务配置
OVERSEAS_IP_SERVICE_URL = 'http://overseasipservice.com/api/getip'

# 海外IP更新频率（秒）
OVERSEAS_IP_UPDATE_INTERVAL = 600