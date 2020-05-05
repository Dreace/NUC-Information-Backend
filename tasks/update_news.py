# from redis_connect import redis_session as session
import json
import logging
import re
import traceback

import bs4
import html2text as ht
import requests

from utils.redis_connections import redis_news
from utils.scheduler import scheduler

type_dic = {"1013": "zbxw", "1014": "tzgg", "1354": "xshd"}
name_dic = {"1013": "news", "1014": "notice", "1354": "academic"}


def update_article(type_id):
    import time
    if time.localtime(time.time())[3] < 7:
        return
    type_ = type_dic[type_id]
    type_name = name_dic[type_id]
    logging.info("开始更新 " + type_name)
    text_maker = ht.HTML2Text()
    text_maker.ignore_links = True
    session = requests.session()
    article_url = "http://www.nuc.edu.cn/index/" + type_ + ".htm"
    articles = []
    while True:
        article_html = session.get(article_url)
        soup = bs4.BeautifulSoup(article_html.content, "html.parser")
        article_list = soup.find_all(class_="list_con_rightlist")
        article_list_a_tag = article_list[0].find_all("a")
        flag = True
        repeat_count = 0
        for a in article_list_a_tag:
            if "class" not in a.attrs.keys():
                try:
                    res = re.search(type_id + r"/([0-9]{0,}).htm", a["href"])
                    if not res:
                        continue
                    news_id = res.group(1)
                    if redis_news.exists(type_name + news_id):
                        # if redis_server.llen(type_name+"_list")>0 and id == json.loads(redis_server.lindex(type_name+"_list",0))["id"]:
                        repeat_count += 1
                        if repeat_count > 3:
                            break
                        continue
                    news = session.get("http://www.nuc.edu.cn/info/" + type_id + "/" + news_id + ".htm")
                    news_soup = bs4.BeautifulSoup(news.content, "html.parser")
                    news_with_id = news_soup.find_all("div", {"id": re.compile(r"vsb_content")})
                    html = str(news_with_id[0]).replace("/__local", "http://www.nuc.edu.cn/__local")
                    text = text_maker.handle(html)
                    news_time = news_soup.find_all(style="line-height:400%;color:#444444;font-size:14px")[0]
                    res_time = re.search(r"时间：(.*)作者", str(news_time))
                    time = res_time.group(1).strip(" ")
                    articles.append(json.dumps({"id": news_id, "date": a.next_sibling.string, "title": a["title"]}))
                    redis_news.set(type_name + news_id,
                                   json.dumps({"time": time, "title": a["title"], "content": text}))
                    logging.info("添加 " + a["title"])

                except:
                    logging.error(traceback.format_exc())
                    logging.error("%s %s" % (a["title"], a["href"]))
            elif a["class"][0] == "Next":
                flag = False
                if a.string == "下页":
                    article_url = "http://www.nuc.edu.cn/index/" + type_ + "/" + a["href"].replace(type_, "").replace(
                        "/", "")
        if flag:
            break
    for x in reversed(articles):
        redis_news.lpush(type_name + "_list", x)
    logging.info("完成更新 " + type_name)


def update_news():
    update_list = ["1013", "1014", "1354"]
    for i in update_list:
        update_article(i)


scheduler.add_job(update_news, 'interval', minutes=10)
