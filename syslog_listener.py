# -*- coding: utf-8 -*-
import argparse
import logging
import SocketServer
from logging.handlers import RotatingFileHandler
from logparser import SyslogMessage, ParseError
import redis
import os
import sys

listenPort = 514
hourOfTTL=72
debugLevel = logging.INFO
host=os.getenv('BQAUTH_REDIS_HOST', 'localhost')
port = os.getenv('BQAUTH_REDIS_PORT', '6379')

redis_conn = redis.StrictRedis(host=host, port=port, db=0)


LOG_FILENAME = './logging/syslog.log'
# Set up a specific logger with our desired output level
logger = logging.getLogger('syslog_listener')
# Add the log message handler to the logger
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=7)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())




class SyslogUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            data = bytes.decode(self.request[0].strip())
            socket = self.request[1]
            data = str(data).decode('utf-8')
            message = SyslogMessage.parse(data)
            logger.info("syslog message:type={0} subtype={1} action={2} usermac={3}".format(
                message.log_type, message.log_subtype, message.log_action,message.log_stamac))
            if (message.log_type == u'event' and 
               message.log_subtype == u'wireless' and 
               (message.log_action == u'"client-authentication"' or 
                message.log_action == u'"client-disconnected-by-wtp"' or
                message.log_action == u'"client-leave-wtp"')):
                usermac = message.log_stamac
                self.refresh_cache(usermac, message.log_action)
        except ParseError as e:
            logger.error(e)
        except UnicodeDecodeError:
            logger.error("UnicodeDecodeError, failed to decode the received data")


    def refresh_cache(self, usermac, action):
        logger.debug("refresh_cache: {0} since {1}".format(usermac, action))
        usermac = usermac.lower 
        if redis_conn.exists(usermac):
            logger.info("Refresh the user auth cache {0}".format(usermac))
            redis_conn.expire(usermac, hourOfTTL * 3600)



def run():
#    handler = RotatingFileHandler(, maxBytes=10000000, backupCount=7)
#    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
#    handler.setFormatter(formatter)
    logger.setLevel(debugLevel)
#    logging.basicConfig(level=debugLevel,
#                    format="%(asctime)s %(levelname)s: %(message)s",
#                    handlers=[handler,logging.StreamHandler()])
    logger.info("Binqsoft syslog listener is running on the TCP port {0}".format(listenPort))
    logger.info("The default TTL of authentication session is {0} hours".format(hourOfTTL))
    server = SocketServer.UDPServer(("0.0.0.0", listenPort), SyslogUDPHandler)
    server.serve_forever(poll_interval=0.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=514, help="TCP listen port, the default is 514")
    parser.add_argument("-t", "--ttl", type=int, default=72, help="hours of session TTL, the default is 72")
    parser.add_argument("-d", "--debug", type=int, default=0, help="debug level: 0 is INFO, 1 is DEBUG")
    
    args = parser.parse_args()
    hourOfTTL = args.ttl
    listenPort = args.port
    if args.debug == 0:
        debugLevel = logging.INFO
    if args.debug >= 1:
        debugLevel = logging.DEBUG

    try:
        run()
    except KeyboardInterrupt:
        sys.exit()




