import re
import traceback
from urllib.parse import quote

import bs4
import requests
from flask import request
from gevent.pool import Pool

from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.need_proxy import need_proxy
from utils.decorators.request_limit import request_limit
from utils.exceptions import custom_abort
from utils.gol import global_values
from . import api, config

session = requests.session()
session.verify = False

requests.packages.urllib3.disable_warnings()


@api.route('/library/search/name/<string:keyword>', methods=['GET'])
@check_sign({'type', 'page'})
@request_limit()
@need_proxy()
@cache({'type', 'page'})
def handle_library_search_by_name(keyword: str):
    book_type = request.args.get('type', '正题名')
    page = request.args.get('page', '1')
    url = 'http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/bk_s_Q_fillpage.asp?q=%s=[[*%s*]]' \
          '&nmaxcount=&nSetPageSize=10&orderby=&Research=1&page=%s&opt=1' % (quote(book_type), quote(keyword), page)
    content = session.get(url, headers={'Cookie': global_values.get_value('vpn_cookie')}).content.decode(
        'utf-8')
    re_book_ids = re.findall(r"ShowItem\('([0-9]*)'\)", content)
    records_group = re.search('共([0-9]*)条记录', content)
    if not records_group:
        custom_abort(-6, '无结果')
    records = records_group.group(1)
    pool = Pool(10)
    book_list = pool.map(book_detail, re_book_ids)
    return {
        'code': 0,
        'data': {
            'records': records,
            'page': page,
            'recordsPerPage': len(book_list),
            'list': book_list
        }
    }


@api.route('/library/search/isbn/<string:isbn>', methods=['GET'])
@check_sign({'page'})
@request_limit()
@need_proxy()
@cache({'page'})
def handle_library_search_by_isbn(isbn: str):
    page = request.args.get('page', '1')
    if len(isbn) != 13 and len(isbn) != 10:
        custom_abort(-6, '无效的 ISBN 编号')
    if len(isbn) == 10:
        isbn = isbn[:1] + '-' + isbn[1:5] + '-' + isbn[5:9] + '-' + isbn[9:]
    else:
        isbn = isbn[:3] + '-' + isbn[3:4] + '-' + isbn[4:8] + '-' + isbn[8:12] + '-' + isbn[12:]
    url = 'http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/bk_s_Q_fillpage.asp?q=标准编号=[[%s*]]' \
          '&nmaxcount=&nSetPageSize=10&orderby=&Research=1&page=%s&opt=1' % (quote(isbn), page)
    content = session.get(url, headers={'Cookie': global_values.get_value('vpn_cookie')}).content.decode(
        'utf-8')
    re_book_ids = re.findall(r"ShowItem\('([0-9]*)'\)", content)
    records_group = re.search('共([0-9]*)条记录', content)
    if not records_group:
        custom_abort(-6, '无结果')
    records = records_group.group(1)
    pool = Pool(10)
    book_list = pool.map(book_detail, re_book_ids)
    return {
        'code': 0,
        'data': {
            'records': records,
            'page': page,
            'recordsPerPage': len(book_list),
            'list': book_list
        }
    }


@api.route('/library/books/<string:book_id>', methods=['GET'])
@check_sign(set())
@request_limit()
@need_proxy()
@cache(set())
def get_book_available_detail(book_id: str):
    url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/showmarc/showbookitems.asp?nTmpKzh=%s" % book_id
    content = session.get(url, headers={'Cookie': global_values.get_value('vpn_cookie')}).content.decode(
        "utf-8")
    soups = bs4.BeautifulSoup(content, "html.parser")
    trs = soups.find_all("tr")
    detail_items = []
    for td in trs[1:]:
        tds = td.find_all("td")
        detail_items.append({
            "number": "".join(tds[1].text.split()),
            "barcode": "".join(tds[2].text.split()),
            "location": "".join(tds[3].text.split()),
            "status": "".join(tds[4].text.split())
        })
    return {
        'code': 0,
        'data': detail_items
    }


def book_detail(book_id) -> dict:
    url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/showmarc/table.asp?nTmpKzh=%s" % book_id
    content = session.get(url, headers={'Cookie': global_values.get_value('vpn_cookie')}).content
    soups = bs4.BeautifulSoup(content, "html.parser")
    details = soups.find(id="tabs-2").find_all("tr")
    url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/BK_getKJFBS.asp"
    post_data = {"nkzh": book_id}
    content = session.post(url, data=post_data,
                           headers={'Cookie': global_values.get_value('vpn_cookie')}).content.decode()
    detail_dict = {"id": book_id, "available_books": content}
    for i in details:
        tds = i.find_all("td")
        if tds[0].text.strip() == "010":
            info = tds[2].text.strip().split("@")
            for j in info:
                if len(j) < 1:
                    continue
                if j[0] == "a":
                    detail_dict["ISBN"] = j[1:]
                    detail_dict["cover_url"] = douban_book_cover(j[1:])
        elif tds[0].text.strip() == "200":
            info = tds[2].text.strip().split("@")
            for j in info:
                if len(j) < 1:
                    continue
                if j[0] == "a":
                    detail_dict["name"] = j[1:]
                elif j[0] == "f":
                    detail_dict["author"] = j[1:]
                elif j[0] == "g":
                    detail_dict["translator"] = j[1:]
        elif tds[0].text.strip() == "210":
            info = tds[2].text.strip().split("@")
            for j in info:
                if len(j) < 1:
                    continue
                if j[0] == "c":
                    detail_dict["press"] = j[1:]
                elif j[0] == "d":
                    detail_dict["year"] = j[1:]
                elif j[0] == "g":
                    detail_dict["translator"] = j[1:]
        elif tds[0].text.strip() == "330":
            info = tds[2].text.strip().split("@")
            for j in info:
                if len(j) < 1:
                    continue
                if j[0] == "a":
                    detail_dict["introduction"] = j[1:]
    if "cover_url" not in detail_dict.keys():
        detail_dict[
            "cover_url"] = "https://img1.doubanio.com/f/shire/5522dd1f5b742d1e1394a17f44d590646b63871d/pics/book" \
                           "-default-lpic.gif"
    return detail_dict


def douban_book_cover(isbn: str) -> str:
    default_url = "https://img1.doubanio.com/f/shire/5522dd1f5b742d1e1394a17f44d590646b63871d/pics/book-default-lpic" \
                  ".gif"
    try:
        response = session.get(
            "https://api.douban.com/v2/book/isbn/{}?apikey=054022eaeae0b00e0fc068c0c0a2102a".format(isbn),
            headers=config.douban_headers
        )
        if response.status_code != 200:
            return default_url
        return response.json().get('image', default_url)
    except requests.RequestException:
        traceback.print_exc()
        return default_url
