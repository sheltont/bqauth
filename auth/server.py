# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, make_response, redirect, session
import sys
import base64
import datetime
import requests
import time
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Generated with: import os; os.urandom(24)
app.secret_key = '\xf7h\xcf\x9c\xf9=\xbc\x11\x7f+\xe7g\x1cm\xafo,ICWc\x12\xe6\xff'


# VERY = 'http://192.168.10.1:1000/fgtauth&'
COOKIE_KEEP = 3



# http://192.168.9.107/?login&
# post=http://192.168.10.1:1000/fgtauth&
# magic=0206038ec0e86a2b&usermac=a4:5e:60:dc:ed:a1&
# apmac=08:5b:0e:ec:74:be&apip=192.168.0.181&
# userip=192.168.10.7&device_type=mac

@app.route('/', methods=['GET'])
def login():
    app.logger.debug(request.args)
    app.logger.debug(request.headers)
    #log_request(request)

    post_url = request.args.get('post')
    magic = request.args.get('magic')
    username = request.cookies.get('username')
    password = request.cookies.get('password')

    app.logger.debug("username: {0}, password: {1}".format(username, password))

    if username and password:
        if 'visited_this_page' in session:
            app.logger.debug("visited_this_page is in the session")
            resp = make_response(render_template('login.html', post_url=post_url, magic=magic))
            #resp.set_cookie('username', '', expires=0)
            #resp.set_cookie('password', '', expires=0)
            return resp
        else:
            session['visited_this_page'] = True
            app.logger.debug("visited_this_page is None, set it to True")
            resp = make_response(render_template('login.html', post_url=post_url, magic=magic))
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=COOKIE_KEEP)
            resp.set_cookie('username', username, expires=expire_date)
            resp.set_cookie('password', password, expires=expire_date)
            app.logger.info("authenticate the user " + username)
            return resp
    return render_template('login.html', post_url=post_url, magic=magic)


def log_request(request):
    post_url = request.args.get('post')
    magic = request.args.get('magic')
    usermac = request.args.get('usermac')
    apmac = request.args.get('apmac')
    apip = request.args.get('apip')
    userip = request.args.get('userip')
    device_type = request.args.get('device_type')
    username = request.cookies.get('username')
    password = request.cookies.get('password')

    output = "\npost_url: {0}\nmagic: {1}\nusermac: {2}\napmac: {3}\napip: {4}\nuserip: {5}\ndevice_type: {6}\nusername: {7}";
    output = output.format(post_url, magic, usermac, apmac, apip, userip, device_type, username)
    app.logger.info(output)


def parse_commands():


if __name__ == '__main__':
    handler = RotatingFileHandler('./logging/bqauth.log', maxBytes=1000000, backupCount=7)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.info("Binqsoft authentication portal is running")
    app.run(host='0.0.0.0', port=80, debug=True)
