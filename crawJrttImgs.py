import json
from multiprocessing.pool import Pool
from urllib.parse import urlencode
from hashlib import md5
import re

import os
import pymongo as pymongo
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup
from config1 import *

# 新建MongoDB对象
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

## 抓取索引页
def get_page_index(offset, keyword):
    data = {
        "offset": offset,
        "format": "json",
        "keyword": keyword,
        "autoload": "true",
        "count": "20",
        "cur_tab": "3"
    }
    url = "https://www.toutiao.com/search_content/?" + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页失败")
        return None

## 解析索引页，拿出字文章链接
def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

## 抓取详情页
def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # 网页文字是text
        return None
    except RequestException:
        print("请求详情页失败")
        return None


## 解析详情页，获取图片链接
def parse_page_detail(html, url):
    soup = BeautifulSoup(html, "lxml")
    title = soup.select('title')[0].get_text()
    # print(title)
    image_pattern = re.compile('var gallery = (.*?);', re.S)
    result = re.search(image_pattern, html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_img(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }

## 保存到MonggoDB的方法
def save_to_mongo(result):
    if result and db[MONGO_TABLE].insert(result):
        print('保存到mongodb成功', result)
        return True
    return False

## 下载图片
def download_img(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.content # 图片是content
            save_img(content)
            print("下载图片" + url + "成功")
        return None
    except RequestException:
        print("下载图片页失败")
        return None

## 保存图片
def save_img(content):
    file_path = '{0}/downloadTouTiaoJiePaiImgs/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path,"wb") as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_index(offset , KEY_WORD)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            save_to_mongo(result)


if __name__ == '__main__':
    group = [20*x for x in range(GROUP_START, GROUP_END+1)]
    pool =Pool()
    pool.map(main, group)
