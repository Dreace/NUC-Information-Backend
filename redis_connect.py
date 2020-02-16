import redis

from global_config import redis_password, redis_host, redis_port

redis_news = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                               encoding='utf8', decode_responses=True, db=2)

redis_request_limit = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                                        encoding='utf8', decode_responses=True, db=3)

redis_token = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                                encoding='utf8', decode_responses=True, db=4)

redis_session = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                                  encoding='utf8', decode_responses=True, db=0)

redis_cache = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                                encoding='utf8', decode_responses=True, db=6)

