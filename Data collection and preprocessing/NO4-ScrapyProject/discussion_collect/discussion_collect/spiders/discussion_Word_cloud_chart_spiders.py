""" 
此子项目用于实现词云图的设计，词云图设计是一种数据可视化的技术，使用python 而非findebi工具。
对清洗后的详细页内容中的正文和评论（英文内容）分别进行词云生成，提取各自的十大热点词汇，生成组合式词云图片，
图片标题用中文描述，帮助作者了解正文核心主题和评论舆论方向，以便后续发布的内容进行优化和改进。
"""
""" 
此子项目用于提取英文正文/评论中的**纯名词**热点词汇，生成柱状图（中文标题）
"""
""" 
此子项目用于提取英文正文/评论中的纯名词热点词汇，生成柱状图（中文标题）
无需nltk库，通过手动过滤实现名词筛选
"""
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from scrapy import Spider

# 配置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 非名词过滤表（覆盖代词/副词/介词/连词/助动词等）
NON_NOUNS = {
    # 代词/限定词
    'i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'hers',
    'it', 'its', 'we', 'us', 'our', 'ours', 'they', 'them', 'their', 'theirs', 'this', 'that',
    'these', 'those', 'all', 'any', 'both', 'each', 'few', 'many', 'much', 'none', 'some', 'such',
    'a', 'an', 'the', 'every', 'no', 'neither', 'either', 'other', 'another',
    # 副词
    'here', 'there', 'when', 'where', 'why', 'how', 'now', 'then', 'soon', 'often', 'always',
    'never', 'maybe', 'perhaps', 'quite', 'very', 'too', 'so', 'just', 'almost', 'already',
    # 介词/连词
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over',
    'under', 'and', 'or', 'but', 'if', 'because', 'as', 'while', 'until', 'since', 'though',
    # 助动词/情态动词
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
    'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
    # 业务无效词
    '未获取到信息', 'request', 'failed', 'parse', 'error', 'content', 'comment', 'unknown', 'user'
}

# 2. 名词特征辅助筛选（排除动词/形容词后缀）
VERB_ADJ_SUFFIX = ['ing', 'ed', 'en', 'able', 'ible', 'ful', 'less', 'ive', 'ous', 'ly']

class DiscussionSpider(Spider):
    name = 'discussion_Word_cloud_chart_spiders'
    
    # 路径配置（和之前一致）
    input_csv_path = os.path.join('data', 'csv', 'discussion_Detailed_Page_cleaned.csv')
    output_img_path = os.path.join('data', 'images', 'content_comment_nouns_top10_en.png')
    comment_separator = '|||'
    
    def start_requests(self):
        """核心执行逻辑：读取CSV→过滤名词→生成图表"""
        # 检查输入文件
        if not os.path.exists(self.input_csv_path):
            self.logger.error(f"输入CSV不存在：{self.input_csv_path}")
            return
        
        # 读取CSV
        try:
            df = pd.read_csv(
                self.input_csv_path,
                encoding='utf-8-sig',
                usecols=['清洗后的正文内容', '清洗后的评论内容列表']
            )
            self.logger.info(f"读取到 {len(df)} 条有效记录")
        except Exception as e:
            self.logger.error(f"读取CSV失败：{str(e)}")
            return
        
        # 处理文本+筛选名词
        content_nouns = self._extract_nouns(df['清洗后的正文内容'], is_content=True)
        comment_nouns = self._extract_nouns(df['清洗后的评论内容列表'], is_content=False)
        
        # 生成纯名词柱状图
        self._generate_chart(content_nouns, comment_nouns)
        
        # 输出Top10名词
        self._print_top10_nouns(content_nouns, comment_nouns)
        
        self.logger.info(f"纯名词图表已保存：{os.path.abspath(self.output_img_path)}")
        return
    
    def _extract_nouns(self, text_series, is_content):
        """提取文本中的纯名词（无nltk版）"""
        # 过滤无效值
        invalid = ['', ' ', '未获取到正文内容', '未获取到评论内容', '请求失败', '解析失败',
                   'No content', 'No comments', 'Request failed', 'Parse error']
        valid_text = text_series.dropna().loc[~text_series.isin(invalid)]
        
        # 合并文本
        if not is_content:
            # 处理评论：拆分列表+移除用户名前缀
            clean_comments = []
            for comment_str in valid_text:
                for c in comment_str.split(self.comment_separator):
                    clean_c = re.sub(r'^[^:]+:\s*', '', c).strip()
                    clean_comments.append(clean_c)
            combined_text = ' '.join(clean_comments)
        else:
            combined_text = ' '.join(valid_text.tolist())
        
        # 清洗文本：小写+移除非字母+拆分单词
        combined_text = combined_text.lower()
        combined_text = re.sub(r'[^a-zA-Z\s]', ' ', combined_text)
        words = combined_text.split()
        
        # 筛选名词：核心逻辑
        nouns = []
        for word in words:
            # 条件1：排除非名词表中的词
            if word in NON_NOUNS:
                continue
            # 条件2：长度≥2（排除单字母）
            if len(word) < 2:
                continue
            # 条件3：排除动词/形容词后缀
            if any(word.endswith(suffix) for suffix in VERB_ADJ_SUFFIX):
                continue
            # 条件4：排除纯数字
            if word.isdigit():
                continue
            # 符合所有条件 → 判定为名词
            nouns.append(word)
        
        # 统计名词词频
        return dict(Counter(nouns))
    
    def _generate_chart(self, content_nouns, comment_nouns):
        """生成纯名词Top10柱状图"""
        # 创建输出目录
        os.makedirs(os.path.dirname(self.output_img_path), exist_ok=True)
        
        # 提取Top10
        content_top10 = Counter(content_nouns).most_common(10)
        comment_top10 = Counter(comment_nouns).most_common(10)
        
        # 画布设置
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('正文VS评论Top10纯名词（英文）', fontsize=20, fontweight='bold', y=0.95)
        
        # 正文名词Top10
        if content_top10:
            words = [w[0] for w in content_top10][::-1]
            counts = [w[1] for w in content_top10][::-1]
            ax1.barh(words, counts, color='#009688', alpha=0.8)
            ax1.set_title('正文Top10纯名词', fontsize=16, fontweight='bold')
            ax1.set_xlabel('出现次数', fontsize=12)
            # 显示数值标签
            for i, c in enumerate(counts):
                ax1.text(c + 0.2, i, str(c), va='center', fontsize=10)
        else:
            ax1.text(0.5, 0.5, '无有效名词数据', ha='center', va='center', fontsize=14)
            ax1.set_title('正文Top10纯名词', fontsize=16, fontweight='bold')
        
        # 评论名词Top10
        if comment_top10:
            words = [w[0] for w in comment_top10][::-1]
            counts = [w[1] for w in comment_top10][::-1]
            ax2.barh(words, counts, color='#FF5722', alpha=0.8)
            ax2.set_title('评论Top10纯名词', fontsize=16, fontweight='bold')
            ax2.set_xlabel('出现次数', fontsize=12)
            # 显示数值标签
            for i, c in enumerate(counts):
                ax2.text(c + 0.2, i, str(c), va='center', fontsize=10)
        else:
            ax2.text(0.5, 0.5, '无有效名词数据', ha='center', va='center', fontsize=14)
            ax2.set_title('评论Top10纯名词', fontsize=16, fontweight='bold')
        
        # 保存图片
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        plt.savefig(self.output_img_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _print_top10_nouns(self, content_nouns, comment_nouns):
        """日志输出Top10纯名词"""
        self.logger.info("\n===== 正文Top10纯名词（英文） =====")
        content_top10 = Counter(content_nouns).most_common(10)
        if content_top10:
            for idx, (word, count) in enumerate(content_top10, 1):
                self.logger.info(f"{idx}. {word} - {count}次")
        else:
            self.logger.info("无有效正文名词")
        
        self.logger.info("\n===== 评论Top10纯名词（英文） =====")
        comment_top10 = Counter(comment_nouns).most_common(10)
        if comment_top10:
            for idx, (word, count) in enumerate(comment_top10, 1):
                self.logger.info(f"{idx}. {word} - {count}次")
        else:
            self.logger.info("无有效评论名词")