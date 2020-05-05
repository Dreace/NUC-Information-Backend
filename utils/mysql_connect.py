from global_config import mysql_host, mysql_password, mysql_user
import pymysql

classroom_db = pymysql.connect(mysql_host, mysql_user, mysql_password, "classroom", charset='utf8')
classroom_cursor = classroom_db.cursor()

course_db = pymysql.connect(mysql_host, mysql_user, mysql_password, "course", charset='utf8')
course_cursor = course_db.cursor()

exam_db = pymysql.connect(mysql_host, mysql_user, mysql_password, "exam", charset='utf8')
exam_cursor = exam_db.cursor()

notice_db = pymysql.connect(mysql_host, mysql_user, mysql_password, "notices", charset='utf8')
notice_cursor = notice_db.cursor()