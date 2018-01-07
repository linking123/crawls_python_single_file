# -*- coding: utf-8 -*-

from hashlib import md5
import re

import os
from requests.exceptions import RequestException
import requests
import threading


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
class ParsePageDetail(threading.Thread):
    def __init__(self, html):
        threading.Thread.__init__(self)
        self.html = html

    def run(self):
        image_pattern = re.compile('<img.*?data-src="(.*?)" alt', re.S)
        result = re.findall(image_pattern, self.html)
        if result:
            for url in result:
                if url:
                    download_img("https://octodex.github.com" + url)
                else:
                    continue
        return


## 下载图片
def download_img(url):
    try:
        response = requests.get(url)
        # pattern = re.compile('.+/(.*?)\.jpg$', re.S)
        # imgName = re.search(pattern, str(url))
        # if imgName and imgName.group(1) and response.status_code == 200:
        if response.status_code == 200:
            content = response.content  # 图片是content
            # save_img(content, imgName.group(1))
            save_img(content,"")
            print("下载图片" + url + "成功")
        return None
    except RequestException:
        print("下载图片页失败")
        return None


## 保存图片
def save_img(content, imgName):
    # 防止文件名重复可用md5生成随机编码命名
    file_path = '{0}/GitHubCatImgs/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    # 这里我用链接中的文件名
    # file_path = '{0}/GitHubCatImgs/{1}.{2}'.format(os.getcwd(), imgName, 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(content)
            f.close()


def main(url):
    html = get_page_detail(url)
    if html:
        p = ParsePageDetail(html)
        p.start()


if __name__ == '__main__':
    url = "https://octodex.github.com/"
    main(url)
    print("finish")
