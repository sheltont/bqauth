
import os
from urlparse import urlparse

host=os.getenv('BQAUTH_REDIS_HOST', 'localhost')
port = os.getenv('BQAUTH_REDIS_PORT', '6379')
url = os.getenv('DB_PORT')
if url:
	o = urlparse(url)
	host = o.hostname
	port = o.port

REDIS_URL = "redis://{0}:{1}/0".format(host, port)
