#!/bin/bash
# Start the whole system

echo "Starting redis"
redis-server &

echo "redis-cli ping"
redis-cli ping

echo "starting Forti authentication portal"
nohup python auth_handler.py -p 80 &

echo "starting Forti syslog listener"
nohup python syslog_listener.py -p 514 &
