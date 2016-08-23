# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, make_response, redirect, session
import requests
import logging
from urlparse import urlparse
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Generated with: import os; os.urandom(24)
app.secret_key = '\xf7h\xcf\x9c\xf9=\xbc\x11\x7f+\xe7g\x1cm\xafo,ICWc\x12\xe6\xff'


# http://127.0.0.1/?login&post=http://127.0.0.1:1000/fgtauth&magic=04050f8ebce39071&usermac=6c:40:08:bb:8a:5e&apmac=08:5b:0e:ec:74:be&apip=192.168.0.181&userip=192.168.10.4&device_type=mac

# http://192.168.9.107/?login&
# post=http://192.168.10.1:1000/fgtauth&
# magic=0206038ec0e86a2b&usermac=a4:5e:60:dc:ed:a1&
# apmac=08:5b:0e:ec:74:be&apip=192.168.0.181&
# userip=192.168.10.7&device_type=mac

# http://192.168.9.107/?auth=failed

@app.route('/fgtauth', methods=['POST'])
def fgtauth():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    referer = request.headers.get('Referer', None)
    _4Tredir = request.form.get('4Tredir', 'http://www.binq.com')

    if username != 'binqsoft' or password != 'Password01!':
        return redirect(get_redir_url(referer), code=302)

    return make_response(render_template('success.html', redir=_4Tredir))



def get_redir_url(url):
    o = urlparse(url)
    if o.port == None:
        return "{0}://{1}/?Auth=Failed".format(o.scheme, o.hostname)
    return "{0}://{1}:{2}/?Auth=Failed".format(o.scheme, o.hostname, o.port)


if __name__ == '__main__':
    handler = RotatingFileHandler('./logging/fortimock.log', maxBytes=1000000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.info("Fortinet Mock Authenticator is running")
    app.run(host='0.0.0.0', port=8081, debug=True)
