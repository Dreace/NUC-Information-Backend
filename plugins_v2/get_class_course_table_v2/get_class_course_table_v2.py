import json
import logging

from flask import Response
from flask import request

from plugins_v2._login_v2.login_v2 import login
from . import api
from .config import class_course_table_url, NAME, PASSWD


@api.route('/GetClassCourseTable', methods=['GET'])
def handle_get_course_table():
    class_name = request.args.get('class', "")
    res = get_class_course_table(class_name)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_class_course_table(class_name):
    message = "OK"
    code = 0
    data = []
    if len(class_name) < 1:
        code = -6
        message = "关键词不能为空"
    else:
        session = login(NAME, PASSWD)
        if isinstance(session, str):
            code = -2
            message = "查询失败"
            logging.warning("全局账号登录失败：%s" % message)
        else:
            post_data = {
                "xnm": "2019",
                "xqm": "12",
                "xqh_id": "01",
                "jg_id": "N07",
                "zyh_id": "N07N080901",
                "bh_id": class_name,
                "_search": "false",
                "queryModel.showCount": "1",
            }
            pre_data = session.post("http://222.31.49.139/jwglxt/kbdy/bjkbdy_cxBjkbdyTjkbList.html?gnmkdm=N214505",
                                    data=post_data).json()
            if not pre_data["items"]:
                code = -6
                message = "无效的班级号"
            else:
                post_data = {
                    "xnm": 2019,
                    "xqm": 12,
                    "xqh_id": "01",
                    "njdm_id": pre_data["items"][0]["njdm_id"],
                    "zyh_id": "N07N080901",
                    "bh_id": class_name,
                    "tjkbzdm": 1,
                    "tjkbzxsdm": 0,
                    "zxszjjs": False
                }

                course_table = session.post(class_course_table_url, data=post_data).json()
                tables = []
                cnt = 0
                name_dict = {}
                for index, table in enumerate(course_table["kbList"]):
                    spited = table["jcor"].split("-")
                    if table["kcmc"] not in name_dict:
                        name_dict[table["kcmc"]] = cnt
                        cnt += 1
                    tables.append({
                        # "Course_Number": table["kch_id"],
                        "Course_Name": table["kcmc"],
                        # "Course_Credit": table["xf"],
                        # "Course_Test_Type": table["khfsmc"],
                        "Course_Teacher": table["xm"],
                        "Course_Week": table["zcd"],
                        "Course_Color": name_dict[table["kcmc"]],
                        "Course_Time": table["xqj"],
                        "Course_Start": spited[0],
                        "Course_Length": int(spited[1]) - int(spited[0]) + 1,
                        "Course_Building": table["xqmc"],
                        "Course_Classroom": table["cdmc"]
                    })
                # for d in course_table["sjkList"]:
                #     tables.append({
                #         "Course_Name": d["sjkcgs"]
                #     })
                # TODO 兼容现有客户端
                data = tables
    return {"message": message, "code": code, "data": data}
