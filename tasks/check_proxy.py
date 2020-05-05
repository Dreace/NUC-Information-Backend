import datetime
import logging

import requests

from global_config import proxy_status_url, get_cookies_url
from utils.scheduler import scheduler
from utils.gol import global_values


def check_proxy():
    try:
        if requests.get(proxy_status_url).content.decode() == "ok":
            global_values.set_value("proxy_status_ok", True)
            vpn_cookies = requests.get(get_cookies_url).content.decode()
            if not global_values.get_value("vpn_cookies"):
                logging.info("已获取 VPN cookies：%s" % vpn_cookies)
            global_values.set_value("vpn_cookies", vpn_cookies)
        else:
            global_values.set_value("proxy_status_ok", False)
            logging.warning("代理离线")
    except:
        global_values.set_value("proxy_status_ok", True)


scheduler.add_job(check_proxy, 'interval', seconds=10, next_run_time=datetime.datetime.now())
