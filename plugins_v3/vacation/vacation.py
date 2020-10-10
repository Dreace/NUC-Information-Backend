import datetime

from utils.decorators.cache import cache
from . import api
from models.vacation import Vacation


@api.route("/vacation", methods=["GET"])
@cache(set())
def handle_vacation():
    vacations = Vacation.query.all()
    now = datetime.datetime.today().date()
    for vacation in vacations:
        if now < vacation.date:
            data = vacation.serialize()
            break
    return {
        "code": 0,
        "data": data
    }
