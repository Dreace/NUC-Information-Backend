import logging
from logging.config import dictConfig

import coloredlogs
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': "[%(asctime)s %(filename)s %(funcName)s %(lineno)d] %(levelname)s %(message)s",
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'log/flask.log',
            'encoding': 'utf8',
            'when': 'midnight',
            # 'maxBytes': 8 * 1024 * 1000,
            'backupCount': 7,
        },
        # 'influx': {
        #     'class': 'influxdb_logging.AsyncInfluxHandler',
        #     "measurement": "root_log", "host": 'localhost', "port": 18086,
        #     "database": 'nuc_information_log'
        # }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})

root_logger = logging.getLogger("root")

coloredlogs.DEFAULT_LEVEL_STYLES = dict(spam=dict(color='green', faint=True),
                                        debug=dict(color='green'),
                                        verbose=dict(color='blue'),
                                        info=dict(color='white'),
                                        notice=dict(color='magenta'),
                                        warning=dict(color='yellow'),
                                        success=dict(color='green', bold=True),
                                        error=dict(color='red'),
                                        critical=dict(color='red', bold=True))
coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                    'hostname': {'color': 'magenta'},
                                    'levelname': {'color': 'black', 'bold': True},
                                    'name': {'color': 'blue'},
                                    'filename': {'color': 'green'},
                                    'funcName': {'color': 'green'},
                                    'lineno': {'color': 'green'},
                                    'programname': {'color': 'cyan'}}
coloredlogs.install(fmt="[%(asctime)s %(filename)s %(funcName)s %(lineno)d] %(levelname)s %(message)s",
                    level='INFO', logger=root_logger)
