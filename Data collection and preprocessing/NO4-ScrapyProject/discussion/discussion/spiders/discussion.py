import csv
import os
import time
from scrapy import Spider, Request

class DiscussionSpider(Spider):
    name = 'discussion'
    allowed_domains = ['discussion.fedoraproject.org']
    start_urls = []
    all_data = []
    target_count = 2000
    current_page = 1

    def start_requests(self):
        self.url_template = "https://discussion.fedoraproject.org/top?page={}&per_page=50&period=all"
        first_page_url = self.url_template.format(self.current_page)
        self.logger.info(f'开始爬取第 {self.current_page} 页：{first_page_url}')
        yield Request(
            url=first_page_url,
            callback=self.parse_topic_list,
            errback=self.handle_error,
            dont_filter=True
        )

    def clean_number(self, text):
        if not text:
            return ''
        return text.strip()

    def parse_topic_list(self, response):
        self.logger.info(f'正在解析第 {self.current_page} 页：{response.url} | 状态码：{response.status}')
        if len(self.all_data) >= self.target_count:
            return

        try:
            topic_rows = response.xpath('//tr[contains(@class, "topic-list-item") or @data-topic-id]')
            if not topic_rows:
                topic_rows = response.xpath('//table//tbody/tr')
            self.logger.info(f'第 {self.current_page} 页发现 {len(topic_rows)} 个话题')

            for row_idx, row in enumerate(topic_rows):
                if len(self.all_data) >= self.target_count:
                    break

                # 标题提取
                title_text = row.xpath('.//td//a[contains(@href, "/t/") and not(contains(@class, "badge-category"))]/text()').extract_first()
                title_href = row.xpath('.//td//a[contains(@href, "/t/")]/@href').extract_first()
                if not title_text and title_href and '/t/' in title_href:
                    title_text = title_href.split('/t/')[-1].split('/')[0].replace('-', ' ')
                title_value = title_text.strip() if title_text else ''

                # 标签提取
                tags = row.xpath('.//a[contains(@class, "discourse-tag") or contains(@class, "tag")]/text()').extract()
                tags = [tag.strip() for tag in tags if tag.strip()]
                tag_value = ', '.join(tags) if tags else ''

                # 作者提取
                author_title = row.xpath('.//img[contains(@class, "avatar")]/@title').extract_first()
                author_value = ''
                if author_title:
                    author_value = author_title.split(' - ')[0].strip() if ' - ' in author_title else author_title.strip()
                if not author_value:
                    author_text = row.xpath('.//a[contains(@href, "/u/")]/text()').extract_first()
                    author_value = author_text.strip() if author_text else ''

                # 评论数提取
                comment_count = row.xpath('.//td[contains(@class, "replies") or position()=3]//span[contains(@class, "number")]/text()').extract_first()
                if not comment_count:
                    comment_text = row.xpath('.//td[contains(@class, "replies") or position()=3]//text()').extract()
                    for text in comment_text:
                        if text.strip():
                            comment_count = text
                            break
                comment_count = self.clean_number(comment_count)

                # 阅读量提取
                view_count = row.xpath('.//td[contains(@class, "views") or position()=4]//span[contains(@class, "number")]/text()').extract_first()
                if not view_count:
                    view_text = row.xpath('.//td[contains(@class, "views") or position()=4]//text()').extract()
                    for text in view_text:
                        if text.strip():
                            view_count = text
                            break
                view_count = self.clean_number(view_count)

                # 发布时间提取
                time_stamp = row.xpath('.//span[contains(@class, "relative-date")]/@data-time').extract_first()
                publish_time = ''
                if time_stamp and time_stamp.isdigit():
                    publish_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_stamp)))
                if not publish_time:
                    time_text = row.xpath('.//span[contains(@class, "relative-date")]/text()').extract_first()
                    publish_time = time_text.strip() if time_text else ''
                if not publish_time:
                    time_text = row.xpath('.//td[contains(@class, "created") or position()=5]//text()').extract()
                    time_text = [t.strip() for t in time_text if t.strip() and not t.strip().isdigit()]
                    publish_time = time_text[0] if time_text else ''

                # 组装数据
                topic_info = {
                    "标题": title_value,
                    "标签": tag_value,
                    "作者": author_value,
                    "总评论数": comment_count,
                    "阅读量": view_count,
                    "发布时间": publish_time
                }
                self.all_data.append(topic_info)
                self.logger.info(f'提取话题成功 | 标题：{title_value} | 累计：{len(self.all_data)}/{self.target_count}')

            # 请求下一页
            if len(self.all_data) < self.target_count:
                self.current_page += 1
                next_page_url = self.url_template.format(self.current_page)
                self.logger.info(f'第 {self.current_page-1} 页解析完成，累计 {len(self.all_data)} 条 | 请求下一页：{next_page_url}')
                yield Request(
                    url=next_page_url,
                    callback=self.parse_topic_list,
                    errback=self.handle_error,
                    dont_filter=True
                )

        except Exception as e:
            self.logger.error(f'列表页解析异常：{e} | 页码：{self.current_page}', exc_info=True)

    def handle_error(self, failure):
        request = failure.request
        self.logger.error(f'请求失败：{request.url} | 错误类型：{failure.type} | 详情：{failure.value}', exc_info=True)
        if len(self.all_data) < self.target_count:
            self.current_page += 1
            next_page_url = self.url_template.format(self.current_page)
            self.logger.info(f'第 {self.current_page-1} 页请求失败，尝试下一页：{next_page_url}')
            yield Request(
                url=next_page_url,
                callback=self.parse_topic_list,
                errback=self.handle_error,
                dont_filter=True
            )

    def closed(self, reason):
        final_data = self.all_data[:self.target_count]
        for idx, item in enumerate(final_data, start=1):
            item["编号"] = idx

        csv_headers = [
            "编号", "标题", "标签", 
            "作者", "总评论数", "阅读量", "发布时间"
        ]

        try:
            save_dir = 'discussion'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            save_path = os.path.join(save_dir, 'fedora_centos_topics.csv')
            with open(save_path, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_headers)
                writer.writeheader()
                writer.writerows(final_data)
            self.logger.info(f'\n爬虫结束原因：{reason}')
            self.logger.info(f'最终保存成功：共 {len(final_data)} 条数据（目标：{self.target_count} 条）')
            self.logger.info(f'文件路径：{os.path.abspath(save_path)}')
        except Exception as e:
            self.logger.error(f'保存 CSV 文件失败：{e}', exc_info=True)