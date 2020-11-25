import redis

from global_config import redis as redis_config

# redis_news = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], password=redis_config['password'],
#                                encoding='utf8', decode_responses=True, db=0)

redis_request_limit = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'],
                                        password=redis_config['password'],
                                        encoding='utf8', decode_responses=True, db=0)

redis_token = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], password=redis_config['password'],
                                encoding='utf8', decode_responses=True, db=1)

redis_session = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'],
                                  password=redis_config['password'],
                                  encoding='utf8', decode_responses=False, db=2)

redis_cache = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], password=redis_config['password'],
                                encoding='utf8', decode_responses=True, db=3)
