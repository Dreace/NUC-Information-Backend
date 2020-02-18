# from redis_connect import redis_session as session
import logging

import psutil as psutil
from influxdb import InfluxDBClient

from scheduler import scheduler

client = InfluxDBClient('localhost', 18086, database="nuc_information_log")

logging.getLogger('apscheduler').setLevel('WARNING')
logging.getLogger('apscheduler').propagate = False


def log_system_info():
    data = [
        {
            "measurement": "system_info_log",
            "fields": {
                "network_out": psutil.net_io_counters().bytes_sent,
                "network_in": psutil.net_io_counters().bytes_recv,
                "disk": psutil.disk_usage("/").percent,
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
            },
        }
    ]
    client.write_points(data)


scheduler.add_job(log_system_info, 'interval', seconds=1)
