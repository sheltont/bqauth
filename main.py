# -*- coding: utf-8 -*-
import sys
import argparse
import cPickle as pickle
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, make_response, redirect, session
#from flask.ext.redis import FlaskRedis
from flask_redis import FlaskRedis
import prpcrypt

app = Flask(__name__)
app.config.from_object('config')
redis_store =  FlaskRedis(app)
crypt = prpcrypt.Crypt("enotsniytfosqnib")

# Generated with: import os; os.urandom(24)
app.secret_key = '\xf7h\xcf\x9c\xf9=\xbc\x11\x7f+\xe7g\x1cm\xafo,ICWc\x12\xe6\xff'


# VERY = 'http://192.168.10.1:1000/fgtauth&'
daysOfTTL = 3
listenPort = 8080


# http://192.168.9.107/?login&
# post=http://192.168.10.1:1000/fgtauth&
# magic=0206038ec0e86a2b&usermac=a4:5e:60:dc:ed:a1&
# apmac=08:5b:0e:ec:74:be&apip=192.168.0.181&
# userip=192.168.10.7&device_type=mac

# http://192.168.9.107/?auth=failed

@app.route('/', methods=['GET'])
def default():
    """
    Flask 请求处理入口
    """
    app.logger.debug(request.args)
    if request.args.has_key('Auth'):
        return handle_auth()
    return handle_login()


def handle_auth():
    """处理验证失败的结果
    测试发现，如果验证没有通过，比如用户输入不正确的用户名或者密码
    Fortinet会再次将用户重定向到Portal，并且请求的参数是?auth=failed
    """
    app.logger.info('handle_auth: ' + request.query_string)
    usermac = get_usermac()
    status = request.args.get('Auth')
    if status and status.lower() == 'Failed':
        if (usermac in session):
            redis_store.delete(usermac)

    # 将用户重定向到登录页面
    resp = make_response(render_template('login.html'))
    return resp

def handle_login():
    """处理登录请求页面
    Fortinet将用户重定向到这个页面，返回表单，收集用户名、密码、是否保留密码等信息
    """
    # 将Fortinet传入的所有信息保存到Session中
    app.logger.info('handle_login: ' + request.query_string)
    usermac = request.args.get('usermac')
    if usermac == None:
        return make_response(render_template('error.html', 
            errorinfo=u"Fortinet未传入UserMac参数，验证无法继续，请联系管理员"))   
    usermac = usermac.lower()
    session['usermac'] = usermac
    session['post'] = request.args.get('post')
    session['magic'] = request.args.get('magic')
    session['apmac'] = request.args.get('apmac')
    session['apip'] = request.args.get('apip')
    session['userip'] = request.args.get('userip')
    session['4Tredir'] = None
    session['device_type'] = request.args.get('device_type')
    
    # 获取缓存的用户名和密码
    userinfo = get_authinfo_from_cache(usermac)
    if userinfo == None:
        return make_response(render_template('login.html', 
            username="", 
            password="", 
            ttl_hour = get_ttl_hour()))

    return make_response(render_template('auth.html', 
            username=userinfo['username'], 
            password=userinfo['password'], 
            post=session['post'], 
            magic=session['magic'], 
            _4Tredir=session['4Tredir']))



@app.route('/auth', methods=['POST'])
def auth():
    """保存用户提交的验证信息
    保存用户验证信息，返回自动登录脚本页面
    """
    app.logger.info('auth: ' + request.query_string)
    username = request.form['username']
    password = request.form['password']
    checked = request.form['checked']
    print "checked " + checked
    usermac = session['usermac']
    post = session['post']
    magic = session['magic']
    _4Tredir = session['4Tredir']
    app.logger.info('username: {0}, password: {1} chars'.format(username, len(password)))
    if username and password:
        if checked: set_authinfo_to_cache(usermac, username, password, get_ttl())
        return make_response(render_template('auth.html', 
            username=username, 
            password=password, 
            post=post, 
            magic=magic, 
            _4Tredir=_4Tredir))
    # 如果用户名或者密码是空，重新收集信息
    return make_response(render_template('login.html', username=username, password=password))


@app.route('/clear', methods=['GET', 'POST'])
def clear():
    """清除某个MAC地址用户的缓存信息
    特殊情况下，需要获取某个用户设备的Mac地址信息，从缓存中清除验证信息
    """

    app.logger.info('clear: ' + request.query_string)
    count = 0
    usermac = request.args.get('usermac')
    if usermac: usermac = usermac.lower()
    if usermac and redis_store.delete(usermac):
        count += 1
    return render_template('clear.html', usermac=usermac, count=count)


def get_authinfo_from_cache(usermac):
    """从缓存中获取验证信息
    """
    username = ""
    password = ""
    userdata = redis_store.get(usermac)
    if userdata:
        userinfo = pickle.loads(userdata)
        username = userinfo['username']
        password = userinfo['password']
        password = crypt.decrypt(password)
        return {'username': username, 'password': password}
    return None

def set_authinfo_to_cache(usermac, username, password, ttl):
    password = crypt.encrypt(password)
    userinfo = {'username': username, 'password': password, 'usermac': usermac}
    userdata = pickle.dumps(userinfo)
    app.logger.info("Cache the auth info for {0}:{1}".format(username, usermac))
    redis_store.set(usermac, userdata, ttl)


def get_usermac():
    mac = session['usermac']
    if mac:
        return mac.lower()
    return None


def get_ttl():
    return (daysOfTTL * 24 * 3600)

def get_ttl_hour():
    return daysOfTTL * 24


def days_of_ttl(arg):
    try:
        var = int(arg)
        return min(1, var)
    except Exception:
        return 3


def run():
    handler = RotatingFileHandler('./logging/bqauth.log', maxBytes=1000000, backupCount=7)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.info("Binqsoft authentication portal is running on the TCP port {0}".format(listenPort))
    app.logger.info("The default TTL of authentication session is {0} days".format(daysOfTTL))
    app.run(host='0.0.0.0', port=listenPort, debug=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080, help="TCP listen port, the default is 8080")
    parser.add_argument("-t", "--ttl", type=int, default=3, help="days of session TTL, the default is 3")
    args = parser.parse_args()
    daysOfTTL = max(1, args.ttl)
    listenPort = args.port
    run()




