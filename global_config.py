import json

import pymysql
from DBUtils.PooledDB import PooledDB

NAME = ""
PASSWD = ""
proxies = {}
proxy_status_url = ""
get_cookies_url = ""
vpn_cookies = ""

redis_host = ""
redis_password = ""
redis_port = 6379

mysql_host = ""
mysql_user = ""
mysql_password = ""

qiniu_access_key = ''
qiniu_secret_key = ''

guest_data = {}
with open("data/guest_data.json", encoding="utf-8") as file:
    guest_data = json.loads(file.read())

no_limit_url = {"GetNews", "v2/fitness/captcha"}
dont_cache_url = {"Token", "ToiCal", "GetNews", "v2/fitness/captcha"}
stopped_list = {"LoginPhyEws", "GetIdleClassroom", "PhysicalFitnessTestLogin"}
need_proxy_url = {"SearchLibrary", "v2/GetCourseTable", "v2/ExportGrade", "v2/GetGrade", "v2/Login",
                  "PhysicalFitnessTestGetScoreList", "PhysicalFitnessTestGetScore", "PhysicalFitnessTestLogin",
                  "GetBookAvailableDetail", "GetClassCourseTable", "SearchLibraryByISBN", "SearchLibrary", "GetCourse",
                  "v2/fitness/list", "v2/fitness/login", "v2/fitness/detail", "v2/fitness/captcha"}

appSecret = ''

mysql_pool = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
    mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
    maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
    maxshared=3,
    # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
    maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
    ping=0,
    # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is
    # created, 4 = when a query is executed, 7 = always
    host=mysql_host,
    port=3306,
    user=mysql_user,
    password=mysql_password,
    database='nuc_info',
    charset='utf8'
)
