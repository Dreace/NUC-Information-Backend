from models.notice import Notice
from utils.decorators.cache import cache
from . import api


@api.route('/notices', methods=['GET'])
@cache(set(), 60)
def handle_notice():
    stick_notices = Notice.query.filter(Notice.is_stick == 1).order_by(Notice.id_.desc()).limit(5)
    not_stick_notices = Notice.query.filter(Notice.is_stick == 0).order_by(Notice.id_.desc()).limit(10)
    return {
        'code': 0,
        'data': {
            'stick': tuple(map(lambda x: x.serialize_without_content(), stick_notices)),
            'notStick': tuple(map(lambda x: x.serialize_without_content(), not_stick_notices))
        }
    }


@api.route('/notices/<int:notice_id>', methods=['GET'])
@cache(set(), 60)
def handle_notice_detail(notice_id: int):
    return {
        'code': 0,
        'data': Notice.query.get(notice_id).serialize()
    }


@api.route('/notices/latest', methods=['GET'])
@cache(set(), 60)
def handle_notice_latest():
    return {
        'code': 0,
        'data': Notice.query.order_by(Notice.id_.desc()).limit(1)[0].serialize()
    }
