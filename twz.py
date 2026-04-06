import requests
import re
from dateutil import parser

headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"}
base_url = "https://www.twz.com/?s=Iran+Israel+conflict"
#base_url = "https://www.tmz.com/search/?q=Iran+Israel+conflict"

response = requests.get(base_url,headers=headers)
print("HTTP响应返回状态码为",response.status_code)
# print("HTTP响应返回内容为",response.text)

from bs4 import BeautifulSoup

# 1. 解析网页，提取所有内容链接
soup = BeautifulSoup(response.text, 'html.parser')
links = []

# 2. 根据实际网页结构调整选择器，这里假设内容链接都在<a>标签中
for link in soup.find_all('a'):
    if link.has_attr('href'):
        href = link['href']
    else:
        continue  # 或 log 跳过
    if "news-features/" in href:
        links.append(href)
print(f"找到 {len(links)} 个内容链接")
for link in links:
    print(link)

# 3. 定义获取单个网页内容函数
import time
def get_single_page_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"}
    response = requests.get(url, headers=headers, timeout=10)
    time.sleep(2.5)  # 遵守robots.txt间隔要求
    soup = BeautifulSoup(response.text, 'html.parser')
    # 根据实际网页结构调整内容提取方式
    content = ''
    for p in soup.find_all('p'):
        content = content + '\n' + p.get_text()
    return content

# 4. 将获取的每篇文章，单独存为一个文件，文件名为时间+标题
def extract_date_before_edt(text):
    """
    从包含 'EDT' 的字符串中提取出现在 'EDT' 之前的日期，并返回 YYYY-MM-DD 格式。
    如果找不到日期或解析失败，返回 None。
    """
    # a. 使用正则找到 EDT 前面的所有内容（直到字符串开头或句子边界）
    #   这里假设 EDT 作为一个独立单词出现（前后可能有空格或标点）
    match = re.search(r'(.*?)\bEDT\b', text, re.IGNORECASE)
    if not match:
        match = re.search(r'(.*?)\bEST\b', text, re.IGNORECASE)
        if not match:
            return None

    # b. 提取 EDT 之前的部分
    before_edt = match.group(1).strip()

    # c. 在 before_edt 中寻找可能的日期（简单策略：取最后一段可能包含数字的文本）
    #   更可靠的方法是尝试解析整个 before_edt，但可能包含无关文字，因此需要更精细的提取。
    #   这里采用一个启发式：尝试匹配常见的日期模式（如 "March 5, 2023", "2023-03-05", "03/05/2023" 等）
    #   如果 before_edt 本身就是一个干净的日期字符串，可以直接解析；否则需要进一步提取。
    
    try:
        dt = parser.parse(before_edt, fuzzy=True)  # fuzzy=True 允许忽略无关文字
        return dt.strftime('%Y-%m-%d')
    except (ValueError, OverflowError):
        # 如果直接解析失败，尝试用正则从 before_edt 中抓取可能的日期模式
        # 常见日期模式：YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY, 等
        # 这里用一个简单正则匹配常见的数字日期格式，你也可以扩展
        date_pattern = r'\b(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b'
        date_match = re.search(date_pattern, before_edt, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1)
            dt = parser.parse(date_str)
            return dt.strftime('%Y-%m-%d')
        else:
            return None

def html2txt(url,content):
    # 1. 分割字符串    
    parts = url.split('/')

    # 3. 提取日期部分（年、月、日），组合成 YYYYMMDD 格式
    date = extract_date_before_edt(content)
    # 4. 提取路径部分（最后一个 / 之后的内容）
    #topic = parts[-2]                                  # 所属专题
    title = parts[-1]                                   # 新闻标题
    file_name = date + "_" + parts[-1] + ".txt"
    with open(file_name, 'w', encoding='utf-8') as f:
        print("正在写入", file_name)
        f.write(content)

# 5. 循环读取所有链接，将内容写入
for link in links:
    html2txt(link, get_single_page_content(link))
