REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
# REDIS_URL = 'redis://localhost:6379/0'

# do not modify anything past here
import os
import urlparse

if 'REDIS_DB' in os.environ:
    REDIS_DB = os.environ['REDIS_DB']

if 'REDIS_PORT' in os.environ:
    parts = urlparse.urlparse(os.environ['REDIS_PORT'])

    if parts.netloc != '':
        if ':' in parts.netloc:
            REDIS_HOST, REDIS_PORT = parts.netloc.split(':', 1)
            REDIS_PORT = int(REDIS_PORT)
        else:
            REDIS_HOST = parts.netloc
    elif parts.path != '':
        if ':' in parts.path:
            REDIS_HOST, REDIS_PORT = parts.path.split(':', 1)
            REDIS_PORT = int(REDIS_PORT)
        else:
            REDIS_HOST = parts.path

