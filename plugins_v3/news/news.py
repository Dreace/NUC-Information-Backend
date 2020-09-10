from flask import request

from models.news import News
from utils.decorators.cache import cache
from . import api


@api.route('/news/<int:type_id>', methods=['GET'])
@cache({'page'}, 60)
def handle_news(type_id: int):
    page_index = request.args.get('page', 1)
    page_size = request.args.get('size', 15)
    news_res = News.query.filter(News.type_ == type_id).order_by(News.publish_time.desc()).paginate(int(page_index),
                                                                                                    int(page_size),
                                                                                                    False)
    return {
        'code': 0,
        'data': tuple(map(lambda x: x.serialize_without_content(), news_res.items))
    }


@api.route('/news/<int:type_id>/<int:news_id>', methods=['GET'])
@cache(set(), 60)
def handle_news_detail(type_id: int, news_id: int):
    return {
        'code': 0,
        'data': News.query.get((type_id, news_id)).serialize()
    }
