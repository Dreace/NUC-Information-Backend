from flask import request

from utils.decorators.cache import cache
from utils.decorators.check_sign import check_sign
from utils.decorators.request_limit import request_limit
from . import api


@api.route('/test', methods=['GET'])
@check_sign(check_args={'name'})
def test():
    return {
        'code': 0,
        'data': request.args.get('name')
    }
