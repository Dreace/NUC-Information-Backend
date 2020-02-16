import json
from typing import List

from flask import Response
from flask import request

from plugins._login.login import login
from . import api
from .config import *


@api.route('/GetGradeMode2', methods=['GET'])
def handle_get_grade_mode_2():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_grade(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetGradeMode2/FailedGrade', methods=['GET'])
def handle_get_fail_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_fail_grade(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_fail_grade(name, passwd):
    message = "OK"
    error = ""
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
        error = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, int):
            code = -1
            error = "账号或密码错误"
            if session == 2:
                message = "账号或密码错误"
            else:
                message = "服务器异常"
        else:
            grade_html = session.get(fail_grade_url).content.decode("gbk")
            soups = bs4.BeautifulSoup(grade_html, "lxml")
            table_tags: List[bs4.BeautifulSoup] = soups.find_all("table", {"class": "titleTop2"})
            grades = {}
            for index, table in enumerate(table_tags):
                grade_list = []
                trs: List[bs4.BeautifulSoup] = table.find_all("tr", {"class": "odd"})
                for tr in trs:
                    tds: List[bs4.BeautifulSoup] = tr.find_all("td")
                    grade_list.append({
                        "Course_Name": tds[2].string.strip(),
                        "Course_Credit": tds[4].string.strip(),
                        "Course_Attribute": tds[5].string.strip(),
                        "Course_Grade": tds[6].text.strip()
                    })
                if index == 0:
                    grades["stillFailed"] = grade_list
                else:
                    grades["usedFailed"] = grade_list
            data = grades
    return {"message": message, "error": error, "code": code, "data": data}


def get_grade(name, passwd):
    message = "OK"
    error = ""
    code = 0
    data = []
    if len(name) < 1 or len(passwd) < 1:
        code = -2
        message = "账号密码不能为空"
        error = "账号密码不能为空"
    else:
        session = login(name, passwd)
        if isinstance(session, int):
            code = -1
            error = "账号或密码错误"
            if session == 2:
                message = "账号或密码错误"
            else:
                message = "服务器异常"
        else:
            # credits = get_credits(session)
            grade_html = session.get(grade_url).content.decode("gbk")
            # grade_html_term = session.get(term_grade_url).content.decode("gbk")
            # term_code = get_term_code(session)
            data = handle_grade_html(grade_html)
    return {"message": message, "error": error, "code": code, "data": data}


def handle_grade_html(html):
    grades = []
    soups = bs4.BeautifulSoup(html, "html5lib")
    a_tags: List[bs4.BeautifulSoup] = soups.find_all("a")
    for a_tag in a_tags:
        table: bs4.BeautifulSoup = a_tag.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
        trs: List[bs4.BeautifulSoup] = table.find_all("tr", {"class": "odd"})
        grade_list = []
        for tr in trs:
            tds = tr.find_all("td")
            grade_list.append({
                "Course_Name": tds[2].string.strip(),
                "Course_Credit": tds[4].string.strip(),
                "Course_Attribute": tds[5].string.strip(),
                "Course_Grade": tds[6].text.strip()
            })
        grades.append({
            "name": a_tag.attrs["name"],
            "grade": grade_list
        })
    return grades
