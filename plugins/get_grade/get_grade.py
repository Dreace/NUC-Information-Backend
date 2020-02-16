import json
import logging
import re
import traceback

from flask import Response
from flask import request

from plugins._login.login import login
from . import api
from .config import *


@api.route('/GetGrade', methods=['GET'])
def handle_get_grade():
    name = request.args.get('name', "")
    passwd = request.args.get('passwd', "")
    res = get_grade(name, passwd)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


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
            credits = get_credits(session)
            grade_html = session.get(grade_url).content.decode("gbk")
            grade_html_term = session.get(term_grade_url).content.decode("gbk")
            term_code = get_term_code(session)
            data = handle_grade_html(grade_html, credits, term_code, grade_html_term)
    return {"message": message, "error": error, "code": code, "data": data}


def get_credits(session):
    r = session.get(credit_url)
    html = r.content.decode("gbk")
    html = re.sub(r"[\r\n\t]", "", html)
    # html = html.replace("\n", "").replace("\r", "").replace("\t", "")
    soups = bs4.BeautifulSoup(html, "lxml")
    tables = soups.select("table.displayTag")
    if len(tables) < 1:
        return {}
    t = tables[0]
    credits = {}
    for tr in t.select("tr"):
        tds = tr.find_all("td")
        if tds and len(tds) > 3:
            credits[tds[0].contents[0].replace(" ", "")] = tds[4].contents[0].replace(" ", "")
    return credits


def handle_grade_html(html, credits, term_code, grade_html_term):
    mm = {}
    soups = bs4.BeautifulSoup(html, "html5lib")
    soups_ = bs4.BeautifulSoup(grade_html_term, "lxml")
    all_term = soups_.find_all(class_="titleTop2")
    grades = []
    i = 0
    titles = soups.find_all(id="tblHead")
    for term in term_code:
        terms = []
        check_course = []
        for t in titles:
            if t.text.find(term["name"] + "计划") != -1:
                # print t.next_sibling.next_sibling.next_sibling.next_sibling.text
                trs = t.next_sibling.next_sibling.next_sibling.next_sibling.find_all("tr")
                # print trs
                for tr in trs:
                    tds = tr.find_all("td")
                    if len(tds) != 5:
                        continue
                    if tds[0].string.strip() not in credits.keys():
                        credits[tds[0].string.strip()] = ""
                    if tds[0].string.strip() in mm.keys() and mm[tds[0].string.strip()] != i:
                        grade = {u"Course_Number": tds[0].string.strip(),
                                 u"Course_Name": tds[1].string.strip() + u"(补考)",
                                 u"Course_Credit": credits[tds[0].string.strip()],
                                 u"Course_Attribute": tds[2].string.strip(),
                                 u"Course_Grade": tds[3].string.strip()}
                    else:
                        mm[tds[0].string.strip()] = i
                        grade = {u"Course_Number": tds[0].string.strip(),
                                 u"Course_Name": tds[1].string.strip(),
                                 u"Course_Credit": credits[tds[0].string.strip()],
                                 u"Course_Attribute": tds[2].string.strip(),
                                 u"Course_Grade": tds[3].string.strip()}
                    check_course.append(tds[0].string.strip())
                    terms.append(grade)
        if terms != []:
            if i < len(all_term):
                trs = all_term[i].find_all("tr")
                for tr in trs:
                    if "class" in tr.attrs.keys():
                        if tr["class"][0] == "odd":
                            tds = tr.find_all("td")
                            if tds[0].string.strip() not in check_course:
                                grade = {u"Course_Number": tds[0].string.strip(),
                                         u"Course_Name": tds[2].string.strip(),
                                         u"Course_Credit": tds[4].string.strip(),
                                         u"Course_Attribute": tds[5].string.strip(),
                                         u"Course_Grade": tds[6].p.string.strip()}
                                terms.append(grade)
            terms.append(calculate_gpa(terms, True))
            terms.append(calculate_gpa(terms))
            grades.append({"name": term["name"], "grade": terms})
        else:
            i -= 1
        i += 1

    return grades


def calculate_gpa(course, without_elective=False):
    g, w = 0, 0
    gpa = 0
    try:
        for c in course:
            if without_elective and c["Course_Attribute"] != "必修":
                continue
            if c["Course_Attribute"] == "GPA":
                continue
            if c["Course_Credit"] == "null":
                continue
            credit = float(c["Course_Credit"])
            if credit == 0:
                continue
            if c["Course_Name"].find("补考") != -1:
                continue
            score = c["Course_Grade"].replace(" ", "")
            if score == "优秀":
                g += 4.5 * credit
            elif score == "良好":
                g += 3.5 * credit
            elif score == "中" or score == "中等":
                g += 2.5 * credit
            elif score == "及格":
                g += 1.5 * credit
            elif score == "不及格":
                pass
            else:
                g += (float(score) / 10 - 5) * credit
            w += credit
        gpa = round(g / w, 2)
    except:
        logging.warning(traceback.format_exc())
    if not gpa > 0:
        gpa = "N/A"
    gpa = {u"Course_Number": " ",
           u"Course_Order": " ",
           u"Course_Name": "本学期平均绩点(必修)" if without_elective else "本学期平均绩点(全部)",
           u"Course_English_Name": "GPA",
           u"Course_Credit": " ",
           u"Course_Attribute": "GPA",
           u"Course_Grade": str(gpa)}
    return gpa
