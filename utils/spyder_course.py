import pprint
import traceback

import pymysql
import requests

from global_config import NAME, PASSWD
from plugins_v3._login.login import login

pp = pprint.PrettyPrinter(indent=2)
cookies = login(NAME, PASSWD)
session = requests.session()
course_db = pymysql.connect("", "", "", "nuc_info", charset='utf8mb4')
course_cursor = course_db.cursor()
post_data = {
    "xnm": "2020",
    "xqm": "3",
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
                        data=post_data, cookies=cookies).json()
for item in pre_data["items"]:
    post_data = {
        "xnm": "2020",
        "xqm": "3",
        "xnmc": "2020-2021",
        "xqmmc": "1",
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
                                data=post_data, cookies=cookies).json()
    for item_j in course_table["kbList"]:
        spited = item_j["jcor"].split("-")
        sql = "INSERT IGNORE INTO `课程-2020-2`(`教学班编号`, `学院`, `课程名`, `教师`, `周次`, `星期`, `开始节次`, " \
              "`时长节次`, `教学楼`, `教室`) " \
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
              (item_j.get("jxb_id"), item.get("jgmc"), item_j.get("kcmc"), item_j.get("xm"), item_j.get("zcd"),
               item_j.get("xqj"),
               spited[0], int(spited[1]) - int(spited[0]) + 1, item_j.get("xqmc"), item_j.get("cdmc"))
        try:
            course_cursor.execute(sql)
            course_db.commit()
            print("{} 完成".format(item["bh_id"]))
        except:
            traceback.print_exc()
            course_db.rollback()
if __name__ == '__main__':
    pass
