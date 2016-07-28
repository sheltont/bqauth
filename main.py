# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, make_response, redirect, session
import base64
import datetime
import requests
import time


app = Flask(__name__)

# Generated with: import os; os.urandom(24)
app.secret_key = '\xf7h\xcf\x9c\xf9=\xbc\x11\x7f+\xe7g\x1cm\xafo,ICWc\x12\xe6\xff'


VERY = 'http://127.0.0.1:5100/'
# VERY = 'http://192.168.10.1:1000/fgtauth&'
COOKIE_KEEP = 30
REDIRECT_URL = 'http://192.168.9.107:5100/success'


# http://192.168.9.107/?login&
# post=http://192.168.10.1:1000/fgtauth&
# magic=0206038ec0e86a2b&usermac=a4:5e:60:dc:ed:a1&
# apmac=08:5b:0e:ec:74:be&apip=192.168.0.181&
# userip=192.168.10.7&device_type=mac

@app.route('/', methods=['GET'])
def login():
    print request.query_string
    post_url = request.args.get('post') if request.args.get('post') else VERY
    magic = request.args.get('magic') if request.args.get('magic') else 'jdhsjdhs'
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    if username and password:
        if 'visited_this_page' in session:
            resp = make_response(render_template('login.html', post_url=post_url, magic=magic))
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            return resp
        else:
            session['visited_this_page'] = True
            resp = make_response(render_template('login.html', post_url=post_url, magic=magic))
            expire_date = datetime.datetime.now()
            expire_date = expire_date + datetime.timedelta(days=COOKIE_KEEP)
            resp.set_cookie('username', username, expires=expire_date)
            resp.set_cookie('password', password, expires=expire_date)
            log_content = username + ' try login at ' + datetime.datetime.now().strftime('%Y-%b-%d %H:%M:%S')
            write_log(log_content)
            return resp
    return render_template('login.html', post_url=post_url, magic=magic)


def write_log(content):
    file_name = "logging/" + time.strftime('%Y-%m-%d', time.localtime()) + '.txt'
    with open(file_name, 'a+') as file:
        file.write(content + '\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    #app.run(debug=True)
