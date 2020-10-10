import datetime
import logging

import requests

from utils.scheduler import scheduler
from utils.session import session

url = "http://222.31.49.139/jwglxt/xtgl/index_initMenu.html?jsdm=xs&_t=1599980405581"


def keep_alive():
    try:
        session.get(url, timeout=10, allow_redirects=False)
    except requests.RequestException:
        logging.warning('无法连接至教务系统')


scheduler.add_job(keep_alive, 'interval', seconds=10, next_run_time=datetime.datetime.now())
