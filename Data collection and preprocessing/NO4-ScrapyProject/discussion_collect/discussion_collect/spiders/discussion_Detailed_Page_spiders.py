""" 
此子项目用于爬取作者标题的详细页内容的文本内容和评论内容，并保存为json格式文件，
后续对JSON文件进行数据处理，过滤所有的特殊符号，只保留纯文本内容和数字以及常用标点符号，
清洗后保存为新的CSV文件，
文件命名格式为：discussion_Detailed_Page_cleaned.csv,
标头为：标题，清洗后的正文内容，清洗后的评论内容列表（多个评论以分隔符分隔），评论带上评论人的用户名。
 """
import csv
import json
import os
import re
import threading
from tqdm import tqdm
from scrapy import Spider, Request
from scrapy.http import HtmlResponse
from urllib.parse import urlparse

class DiscussionDetailedPageSpider(Spider):
    name = 'discussion_Detailed_Page_spiders'
    
    # 文件路径配置
    input_csv_path = os.path.join('data', 'csv', 'fedora_centos_topics_cleaned.csv')
    output_csv_path = os.path.join('data', 'csv', 'discussion_Detailed_Page_cleaned.csv')
    url_field_name = '标题详情URL'
    
    # 特殊字符过滤正则（保留中文、字母、数字、常用标点、空格、小数点）
    ALLOWED_CHARS_PATTERN = r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,，。！？；;:""''（）\(\)-_=+\[\]{}、·…—]'
    # 评论换行阈值（每80个字符换行，可根据需要调整）
    COMMENT_WRAP_LENGTH = 80

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_urls = 0
        self.completed_urls = 0
        self.pbar = None
        self.lock = threading.Lock()
        self.data_cache = []
        
        self.custom_settings = {
            'LOG_LEVEL': 'INFO',
            'DOWNLOAD_DELAY': 0.5,
            'CONCURRENT_REQUESTS': 5,
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def start_requests(self):
        """从清洗后的CSV读取URL，统计总数并生成爬取请求"""
        if not os.path.exists(self.input_csv_path):
            self.logger.error(f"输入文件不存在: {self.input_csv_path}")
            return
        
        url_list = []
        try:
            with open(self.input_csv_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                if self.url_field_name not in reader.fieldnames:
                    self.logger.error(f"CSV中未找到「{self.url_field_name}」字段，请检查字段名！")
                    return
                
                for row in reader:
                    url = row.get(self.url_field_name, '').strip()
                    title = row.get('标题', '未获取到标题').strip()
                    if not url or url == '未获取到信息':
                        self.logger.warning(f"跳过空URL，标题：{title}")
                        continue
                    url_list.append((url, title))
            
            self.total_urls = len(url_list)
            if self.total_urls > 0:
                self.pbar = tqdm(
                    total=self.total_urls,
                    desc="爬取进度",
                    unit="URL",
                    ncols=80,
                    colour="green",
                    leave=True
                )
                self.logger.info(f"共检测到 {self.total_urls} 个有效爬取URL")
            else:
                self.logger.warning("没有可爬取的有效URL")
                return
        
        except Exception as e:
            self.logger.error(f"读取输入CSV失败: {str(e)}")
            return
        
        for url, title in url_list:
            yield Request(
                url=url,
                callback=self.parse_page,
                meta={'title': title},
                errback=self.handle_request_error
            )
    
    def handle_request_error(self, failure):
        """处理请求错误，缓存错误数据"""
        request = failure.request
        self.logger.error(f"请求失败: {request.url}, 错误: {str(failure.value)}")
        
        with self.lock:
            self.data_cache.append({
                'title': request.meta.get('title', '未获取到标题'),
                'cleaned_content': '请求失败',
                'cleaned_comments': '请求失败'
            })
            self._update_progress()
    
    def text_auto_wrap(self, text, wrap_length=None):
        """
        长文本自动换行：
        1. 按指定长度换行（默认80字符）
        2. 优先在标点处换行，保证语义完整
        3. 缩进后续行，提升可读性
        """
        if not text or text.strip() == '':
            return '未获取到信息'
        
        wrap_len = wrap_length or self.COMMENT_WRAP_LENGTH
        # 先按标点分割成短句，再拼接（优先保证语义完整）
        sentence_separators = r'([。！？；;,\n])'
        sentences = re.split(sentence_separators, text)
        # 重组短句（保留分隔符）
        combined_sentences = []
        for i in range(0, len(sentences)-1, 2):
            combined_sentences.append(sentences[i] + (sentences[i+1] if i+1 < len(sentences) else ''))
        if len(sentences) % 2 == 1:
            combined_sentences.append(sentences[-1])
        
        # 逐句拼接，超过长度则换行
        wrapped_lines = []
        current_line = ""
        for sent in combined_sentences:
            if len(current_line + sent) <= wrap_len:
                current_line += sent
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                # 处理超长单句（直接按长度切分）
                if len(sent) > wrap_len:
                    for i in range(0, len(sent), wrap_len):
                        wrapped_lines.append("  " + sent[i:i+wrap_len])  # 缩进后续行
                else:
                    wrapped_lines.append("  " + sent)
                current_line = ""
        if current_line:
            wrapped_lines.append(current_line)
        
        # 拼接所有行，空行过滤
        return '\n'.join([line.strip() for line in wrapped_lines if line.strip()])

    def parse_page(self, response):
        """解析网页内容，提取正文和评论（每个用户评论单独处理+自动换行）"""
        title = response.meta.get('title', '未获取到标题')
        self.logger.info(f"开始解析: {title} - {response.url}")
        
        try:
            preloaded_data = response.css('#data-preloaded::attr(data-preloaded)').get()
            if not preloaded_data:
                self.logger.warning(f"未找到预加载数据: {response.url}")
                self._cache_data(title, '未获取到正文内容', '未获取到评论内容')
                return
            
            preloaded_dict = json.loads(preloaded_data)
            topic_data = None
            for key, value in preloaded_dict.items():
                if key.startswith('topic_') and isinstance(value, str):
                    try:
                        topic_data = json.loads(value)
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not topic_data:
                self.logger.warning(f"未解析到topic数据: {response.url}")
                self._cache_data(title, '未获取到正文内容', '未获取到评论内容')
                return
            
            # 提取并清洗正文（正文也做自动换行）
            posts = topic_data.get('post_stream', {}).get('posts', [])
            content = ''
            if posts:
                raw_content = posts[0].get('cooked', '')
                cleaned_content = self.clean_text(raw_content)
                content = self.text_auto_wrap(cleaned_content)
            
            # 提取评论（每个用户单独一行+自动换行）
            comments = []
            for post in posts[1:]:
                if post.get('username') == 'system':
                    continue
                username = post.get('username', '未知用户')
                raw_comment = post.get('cooked', '')
                cleaned_comment = self.clean_text(raw_comment)
                if cleaned_comment and cleaned_comment != '未获取到信息':
                    # 每个用户评论单独处理：用户名 + 自动换行的评论内容
                    wrapped_comment = self.text_auto_wrap(cleaned_comment)
                    comments.append(f"【{username}】:\n{wrapped_comment}")
            
            # 评论拼接：每个用户占一行，空行分隔
            comments_str = '\n\n'.join(comments) if comments else '未获取到评论内容'
            
            self._cache_data(title, content, comments_str)
            self.logger.info(f"解析完成: {title} - 评论数: {len(comments)}")
            
        except Exception as e:
            self.logger.error(f"解析页面失败 {response.url}: {str(e)}")
            self._cache_data(title, '解析失败', '解析失败')
    
    def _cache_data(self, title, cleaned_content, cleaned_comments):
        """线程安全缓存数据，并更新进度条"""
        with self.lock:
            self.data_cache.append({
                'title': title if title else '未获取到标题',
                'cleaned_content': cleaned_content if cleaned_content else '未获取到正文内容',
                'cleaned_comments': cleaned_comments if cleaned_comments else '未获取到评论内容'
            })
            self._update_progress()
    
    def _update_progress(self):
        """更新进度条"""
        self.completed_urls += 1
        if self.pbar is not None:
            self.pbar.update(1)
            self.pbar.set_description(f"爬取进度 {self.completed_urls}/{self.total_urls}")
    
    def clean_text(self, text):
        """清洗文本：移除HTML标签、过滤特殊字符、清理空格"""
        if not text or text.strip() == '':
            return '未获取到信息'
        
        # 1. 移除HTML标签
        html_pattern = r'<[^>]+>'
        text_without_html = re.sub(html_pattern, '', text)
        
        # 2. 移除转义字符
        text_unescaped = (
            text_without_html
            .replace('\\u003cp\\u003e', '')
            .replace('\\u003c/p\\u003e', '\n')
            .replace('\\u003cbr\\u003e', '\n')
            .replace('\\u003ccode\\u003e', '`')
            .replace('\\u003c/code\\u003e', '`')
            .replace('\\u003cpre\\u003e', '\n')
            .replace('\\u003c/pre\\u003e', '\n')
            .replace('\\n', '\n')
            .replace('\\', '')
        )
        
        # 3. 过滤特殊字符
        cleaned_text = re.sub(self.ALLOWED_CHARS_PATTERN, '', text_unescaped)
        
        # 4. 清理多余空格和换行
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text if cleaned_text else '未获取到信息'
    
    def closed(self, reason):
        """爬虫结束时，写入【每个用户评论单独一行+自动换行】的CSV"""
        if self.pbar is not None:
            self.pbar.close()
        
        self.logger.info(f"\n爬虫结束，原因: {reason}")
        
        if not self.data_cache:
            self.logger.warning("无数据可写入CSV")
            return
        
        output_dir = os.path.dirname(self.output_csv_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入最终格式的文件
        try:
            with open(self.output_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                # 表头说明
                f.write("======= Fedora/CentOS 讨论详情爬取结果 =======\n")
                f.write("格式说明：\n")
                f.write("1. 每条记录包含标题、正文、评论三部分\n")
                f.write("2. 每个用户的评论单独分段，长评论自动分行（缩进显示）\n")
                f.write("3. 评论格式：【用户名】+ 评论内容（按语义分行）\n\n")
                
                # 遍历所有记录写入
                for idx, item in enumerate(self.data_cache, 1):
                    f.write(f"{'='*50}\n")
                    f.write(f"记录{idx} - 标题：{item['title']}\n")
                    f.write(f"{'='*50}\n")
                    f.write(f"清洗后的正文内容：\n{item['cleaned_content']}\n\n")
                    f.write(f"清洗后的评论内容：\n{item['cleaned_comments']}\n\n\n")
            
            self.logger.info(f"优化版CSV已生成: {os.path.abspath(self.output_csv_path)}")
            self.logger.info(f"共生成 {len(self.data_cache)} 条有效记录")
        
        except Exception as e:
            self.logger.error(f"写入CSV失败: {str(e)}")