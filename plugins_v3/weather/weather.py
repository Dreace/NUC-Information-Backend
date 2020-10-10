import datetime

from global_config import weather_key
from models.notice import Notice
from utils.decorators.cache import cache
from utils.session import session
from . import api


@api.route("/weather", methods=["GET"])
@cache(set(), 60)
def handle_weather():
    weather = session.get(
        "https://restapi.amap.com/v3/weather/weatherInfo?city=140108&key={}".format(weather_key)).json()

    notice = Notice.query.order_by(Notice.id_.desc()).limit(1)[0]
    if (datetime.datetime.now() - notice.time).days >= 3:
        notice = ""
    else:
        notice = notice.serialize_without_content()
    return {
        "code": 0,
        "data": {
            "weather": weather,
            "notice": notice
        }
    }
