import random

from models.slide import Slide
from utils.decorators.cache import cache
from . import api


@api.route("/slides", methods=["GET"])
@cache(set())
def handle_slide():
    slides = Slide.query.all()
    slides.sort(key=lambda x: x.index)
    n = random.randrange(0, len(slides))
    slides = slides[n:] + slides[:n]
    return {
        'code': 0,
        'data': list(map(lambda x: x.serialize_without_content(), slides))
    }


@api.route("/slides/<int:slide_id>", methods=["GET"])
@cache(set())
def handle_slide_id(slide_id: int):
    return {
        "code": 0,
        "data": Slide.query.get(slide_id).serialize()
    }
