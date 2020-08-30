import logging
import re
from datetime import datetime

import html2text as ht
import requests
from bs4 import BeautifulSoup

from index import app
from models.news import News
from models.sqlalchemy_db import db
from utils.scheduler import scheduler

session = requests.Session()

types = {
    'zbxw': {
        'id': 1013,
        'selector': {
            'a': 'body > div.list > div.list_con > div.list_con_rightlist > ul > li > a',
            'next': '.Next'
        },
        'url': {
            'index': 'http://www.nuc.edu.cn/index/{}.htm',
            'next': 'http://www.nuc.edu.cn/index/zbxw/{}.htm',
            'detail': 'http://www.nuc.edu.cn/info/1013/{}.htm#tips'
        }
    },
    'tzgg': {
        'id': 1014,
        'selector': {
            'a': 'body > div.list > div.list_con > div.list_con_rightlist > ul > li > a',
            'next': '.Next'
        },
        'url': {
            'index': 'http://www.nuc.edu.cn/index/{}.htm',
            'next': 'http://www.nuc.edu.cn/index/tzgg/{}.htm',
            'detail': 'http://www.nuc.edu.cn/info/1014/{}.htm#tips'
        }
    },
    'xshd': {
        'id': 1354,
        'selector': {
            'a': 'body > div.list > div.list_con > div.list_con_rightlist > ul > li > a',
            'next': '.Next'
        },
        'url': {
            'index': 'http://www.nuc.edu.cn/index/{}.htm',
            'next': 'http://www.nuc.edu.cn/index/xshd/{}.htm',
            'detail': 'http://www.nuc.edu.cn/info/1354/{}.htm#tips'
        }
    }
}

text_maker = ht.HTML2Text()
text_maker.ignore_links = True


def spider_news(type_name: str):
    html_content = session.get(types[type_name]['url']['index'].format(type_name)).content.decode()
    cnt = 0
    while True:
        soup = BeautifulSoup(html_content, 'html.parser')
        a_tags = soup.select(types[type_name]['selector']['a'])
        for a in a_tags:
            re_res = re.search('(\d*).htm', a.attrs['href'])
            news_id = int(re_res.group(1))
            # 判断重复，每页内容也有可能重复
            if News.query.filter(News.type_ == types[type_name]['id'], News.id_ == news_id).all():
                cnt += 1
                # 兼容第一次获取，和后继更新
                if cnt >= 20:
                    return
            else:
                cnt = 0
                detail_content = session.get(types[type_name]['url']['detail'].format(news_id)).content.decode()
                detail_soup = BeautifulSoup(detail_content, 'html.parser')

                title = a.attrs['title'].strip()
                # 时间
                time_text = detail_soup.find(style="line-height:400%;color:#444444;font-size:14px")
                if not time_text:
                    continue
                re_res = re.search('时间：(.*)作者', time_text.text)
                publish_time = datetime.strptime(re_res.group(1).strip(), '%Y年%m月%d日 %H:%M')
                # HTML 转成 Markdown
                news_html = detail_soup.find("div", {"id": re.compile(r"vsb_content")})
                news_html = str(news_html).replace("/__local", "http://www.nuc.edu.cn/__local")
                content = text_maker.handle(news_html)
                news = News(type_=types[type_name]['id'],
                            id_=news_id,
                            title=title,
                            publish_time=publish_time,
                            content=content)
                db.session.add(news)
                db.session.commit()
                logging.info('添加：{}'.format(title))
        next_page_a = soup.select_one(types[type_name]['selector']['next'])
        if not next_page_a:
            break
        re_res = re.search('(\d*).htm', next_page_a.attrs["href"])
        html_content = session.get(types[type_name]['url']['next'].format(re_res.group(1))).content.decode()


def start():
    logging.info('开始更新新闻')
    with app.app_context():
        for name in types.keys():
            spider_news(name)
    logging.info('更新完成')


scheduler.add_job(start, 'interval', seconds=600, next_run_time=datetime.now())
