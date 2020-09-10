import pprint
import time
import traceback

import pymysql

from global_config import NAME, PASSWD
from plugins_v2._login_v2.login_v2 import login

pp = pprint.PrettyPrinter(indent=2)
session = login(NAME, PASSWD)
course_db = pymysql.connect("127.0.0.1", "root", "", "course", charset='utf8mb4')
course_cursor = course_db.cursor()
if isinstance(session, str):
    code = -3
    message = session
else:
    a = "19080741"
    post_data = {
        "xnm": "2019",
        "xqm": "12",
        "xqh_id": "01",
        "njdm_id": "",
        "jg_id": "",
        "zyh_id": "",
        "zyfx_id": "",
        "bh_id": "",
        "_search": "false",
        "queryModel.showCount": "5000",
    }
    pre_data = session.post("http://222.31.49.139/jwglxt/kbdy/bjkbdy_cxBjkbdyTjkbList.html?gnmkdm=N214505",
                            data=post_data).json()
    for item in pre_data["items"]:
        post_data = {
            "xnm": "2019",
            "xqm": "12",
            "xnmc": "2019-2020",
            "xqmmc": "2",
            "xqh_id": "01",
            "njdm_id": item["njdm_id"],
            "zyh_id": item["zyh_id"],
            "bh_id": item["bh_id"],
            "tjkbzdm": "1",
            # "zymc": "物联网工程(2013)",
            "tjkbzxsdm": "0",
            "zxszjjs": True
        }
        course_table = session.post("http://222.31.49.139/jwglxt/kbdy/bjkbdy_cxBjKb.html?gnmkdm=N214505&su=1707004548",
                                    data=post_data).json()
        for item_j in course_table["kbList"]:
            spited = item_j["jcor"].split("-")
            sql = "INSERT IGNORE INTO course.`课程-2020-1`(`教学班编号`, `学院`, `课程名`, `教师`, `周次`, `星期`, `开始节次`, " \
                  "`时长节次`, `教学楼`, `教室`) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                  (item_j.get("jxb_id"),item.get("jgmc"), item_j.get("kcmc"), item_j.get("xm"), item_j.get("zcd"), item_j.get("xqj"),
                   spited[0], int(spited[1]) - int(spited[0]) + 1, item_j.get("xqmc"), item_j.get("cdmc"))
            try:
                course_cursor.execute(sql)
                course_db.commit()
            except:
                traceback.print_exc()
                course_db.rollback()
        time.sleep(1)
