
import os

host=os.getenv('BQAUTH_REDIS_HOST', 'localhost')
port = os.getenv('BQAUTH_REDIS_PORT', '6379')

REDIS_URL = "redis://{0}:{1}/0".format(host, port)
