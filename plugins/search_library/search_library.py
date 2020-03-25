import re
import traceback
from urllib.parse import quote

import requests
from flask import Response
from flask import request
from gevent.pool import Pool

from . import api
from .config import *

requests.packages.urllib3.disable_warnings()
session = requests.session()
session.proxies = proxies
session.verify = False


@api.route('/SearchLibrary', methods=['GET'])
def search_library():
    session.headers = {"Cookie": global_values.get_value("vpn_cookies")}
    book_type = request.args.get("type", "正题名")
    book_name = request.args.get('keyword', "")
    page = request.args.get('page', "1")
    res = search(book_type, book_name, page)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/SearchLibraryByISBN', methods=['GET'])
def search_library_isbn():
    session.headers = {"Cookie": global_values.get_value("vpn_cookies")}
    isbn = request.args.get('keyword', "")
    res = search_by_isbn(isbn)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetBookAvailableDetail', methods=['GET'])
def get_book_available_detail():
    session.headers = {"Cookie": global_values.get_value("vpn_cookies")}
    book_id = request.args.get('BookID', "")
    res = get_available_book_detail(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_available_book_detail(book_id) -> dict:
    message = "OK"
    error = ""
    code = 0
    data = []
    try:
        url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/showmarc/showbookitems.asp?nTmpKzh=%s" % book_id
        content = session.get(url).content.decode("utf-8")
        soups = bs4.BeautifulSoup(content, "html.parser")
        trs = soups.find_all("tr")
        if len(trs) > 1:
            for td in trs[1:]:
                tds = td.find_all("td")
                data.append({"number": "".join(tds[1].text.split()),
                             "barcode": "".join(tds[2].text.split()),
                             "location": "".join(tds[3].text.split()),
                             "status": "".join(tds[4].text.split())})
    except:
        message = "发生异常"
        error = "服务器内部错误"
        code = -1
    return {"message": message, "error": error, "code": code, "data": data}


def search_by_isbn(isbn) -> dict:
    message = "OK"
    error = ""
    code = 0
    data = {}
    if len(isbn) != 13 and len(isbn) != 10:
        message = "参数错误"
        error = "非法的 ISBN 编号"
        code = -1
    else:
        if len(isbn) == 10:
            isbn = isbn[:1] + "-" + isbn[1:5] + "-" + isbn[5:9] + "-" + isbn[9:]
        else:
            isbn = isbn[:3] + "-" + isbn[3:4] + "-" + isbn[4:7] + "-" + isbn[7:12] + "-" + isbn[12:]
        try:
            url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/bk_s_Q_fillpage.asp?q=标准编号=[[%s*]]" \
                  "&nmaxcount=&nSetPageSize=10&orderby=&Research=1&page=1&opt=1" % (quote(isbn))
            content = session.get(url).content.decode('utf-8')
            re_book_ids = re.findall(r"ShowItem\('([0-9]*)'\)", content)
            records_group = re.search(r"共([0-9]*)条记录", content)
            if records_group is None:
                message = "无结果"
                code = -1
                error = "没有找到任何匹配结果"
            else:
                records = records_group.group(1)
                pool = Pool(10)
                book_list = pool.map(get_book_detail, re_book_ids)
                data = {"total_records": records, "page": 1, "page_records": len(book_list), "list": book_list}
        except:
            traceback.print_exc()
            message = "发生异常"
            code = -1
            error = "服务器内部错误"
    return {"message": message, "error": error, "code": code, "data": data}


def search(book_type, keyword, page=1) -> dict:
    message = "OK"
    error = ""
    code = 0
    data = {}
    try:
        url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/bk_s_Q_fillpage.asp?q=%s=[[%s*]]" \
              "&nmaxcount=&nSetPageSize=10&orderby=&Research=1&page=%s&opt=1" % (quote(book_type), quote(keyword), page)
        content = session.get(url).content.decode('utf-8')
        re_book_ids = re.findall(r"ShowItem\('([0-9]*)'\)", content)
        records_group = re.search(r"共([0-9]*)条记录", content)
        if records_group is None:
            message = "无结果"
            code = -1
            error = "没有找到任何匹配结果"
        else:
            records = records_group.group(1)
            pool = Pool(10)
            book_list = pool.map(get_book_detail, re_book_ids)
            data = {"total_records": records, "page": 1, "page_records": len(book_list), "list": book_list}
    except:
        message = "发生异常"
        code = -1
        error = "服务器内部错误"
    return {"message": message, "error": error, "code": code, "data": data}


def get_book_detail(book_id) -> dict:
    url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/showmarc/table.asp?nTmpKzh=%s" % book_id
    content = session.get(url).content
    soups = bs4.BeautifulSoup(content, "html.parser")
    details = soups.find(id="tabs-2").find_all("tr")
    detail_dict = {}
    detail_dict["id"] = book_id
    detail_dict["available_books"] = get_book_available(book_id)
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
            "cover_url"] = "https://img1.doubanio.com/f/shire/5522dd1f5b742d1e1394a17f44d590646b63871d/pics/book-default-lpic.gif"
    return detail_dict


def get_book_available(boo_id) -> str:
    url = "http://222-31-39-3-8080-p.vpn.nuc1941.top:8118//pft/wxjs/BK_getKJFBS.asp"
    post_data["nkzh"] = boo_id
    content = session.post(url, data=post_data).content.decode()
    return content


douban_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "DNT": "1",
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def douban_book_cover(isbn):
    try:
        url = "https://api.douban.com/v2/book/isbn/%s?apikey=0df993c66c0c636e29ecbb5344252a4a" % isbn
        res = requests.get(url, headers=douban_headers, verify=False)
        book_json = json.loads(res.content.decode())
        if "images" in book_json.keys():
            return book_json["images"]["small"]
        else:
            return "https://img1.doubanio.com/f/shire/5522dd1f5b742d1e1394a17f44d590646b63871d/pics/book-default-lpic.gif"
    except:
        traceback.print_exc()
        return "https://img1.doubanio.com/f/shire/5522dd1f5b742d1e1394a17f44d590646b63871d/pics/book-default-lpic.gif"
