import datetime
import logging

import requests

from global_config import proxy_status_url
from scheduler import scheduler
from utils.gol import global_values


def check_proxy():
    try:
        if requests.get(proxy_status_url).content.decode() == "ok":
            global_values.set_value("proxy_status_ok", True)
        else:
            global_values.set_value("proxy_status_ok", False)
    except:
        global_values.set_value("proxy_status_ok", True)


scheduler.add_job(check_proxy, 'interval', seconds=10, next_run_time=datetime.datetime.now())
