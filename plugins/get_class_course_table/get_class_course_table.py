import re

from flask import request
from flask import Response
import json
from . import api
from .config import *
from plugins._login.login import login


@api.route('/GetClassCourseTable', methods=['GET'])
def handle_get_class_course_table():
    class_number = request.args.get('class', "")
    res = get_class_course_table(class_number)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_class_course_table(class_number):
    message = "OK"
    error = ""
    code = 0
    data = []
    session = login("1707004548", "19990920nx")
    if type(session) != type(1):
        url = "http://202.207.177.39:8089/bjKbInfoAction.do?oper=bjkb_xx&xzxjxjhh=2019-2020-1-1&xbjh=%s&xbm=%s" % (
            class_number, class_number)
        content = session.get(url).content.decode('gbk')
        soups = bs4.BeautifulSoup(content, "lxml")
        table_raw = soups.find(class_="displayTag")
        trs = table_raw.find_all("tr")
        pattern = re.compile(r'(.*?)\((.*?),(.*?),(.*?),(.*?)\)')
        course_table_raw = []
        i = 1
        for tr in trs:
            tds = tr.find_all("td", {"valign": "top"})
            if len(tds) == 7:
                j = 1
                for td in tds:
                    text = "".join(td.text.split())
                    if len(text) > 2:
                        text = text.replace("杨晓峰(物理)", "杨晓峰")
                        text = text.replace("杨晓峰(数学)", "杨晓峰")
                        course_table_raw.append({"data": text, "i": i, "j": j})
                    j += 1
                i += 1
        course_name = {}
        m, n = 9, 13
        cnt = 1
        while len(course_table_raw) > 0:
            course_table_raw_t = []
            course_table_t = [[0 for _i in range(m)] for _j in range(n)]
            for k in course_table_raw:
                text = k["data"]
                i = k["i"]
                j = k["j"]
                # print text
                groups = pattern.search(text).groups()
                course_name_striped = groups[0].replace(u"\u00a0", "")
                text_subed = re.sub("(.*?)\(.*?\)", "", text, 1)
                if len(text_subed) > 2:
                    k["data"] = text_subed
                    course_table_raw_t.append(k)
                if course_name_striped in course_name.keys():
                    color = course_name[course_name_striped]
                else:
                    color = cnt
                    course_name[course_name_striped] = color
                    cnt += 1
                course_table_t[i][j] = {
                    "Course_Name": course_name_striped,
                    "Course_Teacher": groups[3],
                    "Course_Week": groups[4],
                    "Course_Color": color,
                    "Course_Time": j,
                    "Course_Start": i,
                    "Course_Length": 1,
                    "Course_Building": groups[1],
                    "Course_Classroom": groups[2]
                }
            course_table_raw = course_table_raw_t
            for i in range(2, 12):
                for j in range(1, 8):
                    if course_table_t[i - 1][j] != 0 and course_table_t[i][j] != 0 \
                            and course_table_t[i - 1][j]["Course_Name"] == course_table_t[i][j]["Course_Name"] \
                            and course_table_t[i - 1][j]["Course_Classroom"] == course_table_t[i][j][
                        "Course_Classroom"]:
                        course_table_t[i][j]["Course_Start"] = course_table_t[i - 1][j]["Course_Start"]
                        course_table_t[i][j]["Course_Length"] += 1
                        course_table_t[i - 1][j] = 0
            for i in course_table_t:
                for j in i:
                    if j != 0:
                        j["Course_Name"] = re.sub(r"_[0-9]\d*", "", j["Course_Name"])
                        data.append(j)
    return {"message": message, "error": error, "code": code, "data": data}
