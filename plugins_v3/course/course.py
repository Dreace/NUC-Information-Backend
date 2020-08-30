import pymysql
from flask import request

from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.request_limit import request_limit
from utils.sql_helper import SQLHelper
from . import api


@api.route('/course', methods=['GET'])
@check_sign({'keywords'})
@request_limit()
@cache({'keywords'})
def handle_course():
    keywords = request.args.get('keywords', '')
    keywords = pymysql.escape_string(keywords)
    keywords_map = ''.join(map(lambda k: '(?=.*%s)' % k, keywords.split(' ')))
    sql = "SELECT * FROM `课程-2020-2` WHERE CONCAT_WS('', `学院`, `课程名`, `教师`) REGEXP '%s^.*$'" % keywords_map
    course_items = []
    for index, row in enumerate(SQLHelper.fetch_all(sql)):
        course_items.append({
            'id': index + 1,
            'department': row['学院'],
            'name': row['课程名'],
            'teacher': row['教师'],
            'weeks': row['周次'],
            'dayOfWeek': row['星期'],
            'start': row['开始节次'],
            'length': row['时长节次'],
            'building': row['教学楼'],
            'classroom': row['教室']
        })
    return {
        'code': 0,
        'data': course_items
    }
