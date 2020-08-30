from flask import request

from utils.decorators.check_sign import check_sign
from . import api


@api.route('/test', methods=['GET'])
@check_sign(check_args={'name'})
def test():
    return {
        'code': 0,
        'data': request.args.get('name')
    }
