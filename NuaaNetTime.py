#!/usr/bin/python
# -*- coding: utf-8 -*-

# 南京航空航天大学校园网服务网页python实现
# 根据http://github.com/0x5e/wechat-deleted-friends修改

import os
import logging
import requests
import re
import time
import xml.dom.minidom
import json
import sys
import math
import subprocess
import ssl
import threading
from bs4 import BeautifulSoup


class NuaaNetTime:

    def __init__(self, name, pswd):
        self.debug = 1
        self.name = name
        self.pswd = pswd
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'Referer': 'http://fuwu.nuaa.edu.cn/',
            'Host': 'fuwu.nuaa.edu.cn'
        }
        self.login()

    # 日志
    def _log(self, str, level = True):
        if self.debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                datefmt='%a, %d %b %Y %H:%M:%S',
                                filename='log.txt',
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
            if level:
                logging.debug('%s ... 成功' % (str))
            else:
                logging.warning('%s ... 失败' % (str))
                logging.debug('[*] 退出程序')
                exit()

    # 运行函数
    def _run(self, str, func, *args):
        if func(*args):
            self._log(str)
        else:
            self._log(str)

    # 封装过的Get方式
    def _get(self, url, data=None):
        session = self.login()
        if session:
            r = session.get(url, headers=self.headers)
            if r.status_code == 200:
                return r.text.encode('utf-8')
            else:
                raise Exception('_get error')

    # 封装过的Post方式
    def _post(self, url, datadata=None):
        session = self.login()
        if session:
            r = session.post(url, data=datadata, headers=self.headers)
            print r.status_code
            if r.status_code == 200:
                return r.text.encode('utf-8')
            else:
                raise Exception('_post error')

    # 登陆 保存cookie
    def login(self):
        self._log('登陆')
        if hasattr(self, 'session'):
            return self.session
        else:
            cookiefile = 'cookie.dat'
            session = requests.session()
            if os.path.exists(cookiefile):
                with open(cookiefile) as f:
                    cookie = json.load(f)
                session.cookies.update(cookie)
                r = session.get('http://fuwu.nuaa.edu.cn/user/home.jhtm', headers=self.headers)
                if self.name in r.text.encode('utf-8'):
                    self.session = session
                    return True
            postdata = {
                'username': self.name,
                'password': self.pswd,
                'code':''
            }
            r = session.post('http://fuwu.nuaa.edu.cn/action/doLogin.do', headers=self.headers, data=postdata)
            if r.json()['status'] == 1:
                with open(cookiefile, 'wb') as f:
                    json.dump(session.cookies.get_dict(), f)
                self.session = session
                return True
            elif r.json()['status'] == -1:
                self._log('错误的用户名或密码', False)
            else:
                self._log('登陆错误，未知错误', False)
            return False

    # 登陆账号信息 本月消费信息
    def getInfo(self):
        html = self._get('http://fuwu.nuaa.edu.cn/user/home.jhtm')
        name = re.findall(r'<li>(.+?)，', html)[0]
        timat = re.findall(r'</span><span class="home_detail">(.+?)</span>', html)
        money = {'shenyu':timat[1], 'xiaofei':timat[2], 'chong':timat[3]}
        user = {'name':name, 'num':self.name}
        return {'user':user, 'money':money}

    # 修改密码
    def changePswd(self, pswd):
        postdata = {
            'username': self.name,
            'oldPass': self.pswd,
            'newPass': pswd
        }
        self._post('http://fuwu.nuaa.edu.cn/action/doChangePw.do', postdata)

    # 扣费记录
    def getKoufei(self, page):
        data = self._get('http://fuwu.nuaa.edu.cn/user/chargeback.jhtm?p=' + str(page))
        soup = BeautifulSoup(data, 'lxml')
        trs = soup.find_all('tr')
        ss = []
        for tr in trs:
            s = []
            ths = tr.find_all('td')
            for th in ths:
                s.append(th.string)
            ss.append(s)
        del ss[0]
        return ss

    # 保存所有扣费记录文件
    def saveKoufei(self):
        html = self._get('http://fuwu.nuaa.edu.cn/user/chargeback.jhtm')
        count = int(re.findall(r'\?p=(.+?)"', html)[-1])
        with open('koufei.txt', 'w+') as f:
            for i in xrange(1, count+1):
                lists = self.getKoufei(i)
                for j in lists:
                    s = ','.join(j)
                    f.write(s.encode('utf-8'))
                    f.write('\n')

    # 充值记录
    def getChong(self, page):
        data = self._get('http://fuwu.nuaa.edu.cn/user/prepaid.jhtm?p=' + str(page))
        soup = BeautifulSoup(data, 'lxml')
        trs = soup.find_all('tr')
        ss = []
        for tr in trs:
            s = []
            ths = tr.find_all('td')
            for th in ths:
                s.append(th.string)
            ss.append(s)
        del ss[0]
        return ss

name = '021210523'
pswd = '99998888'
nnt = NuaaNetTime(name, pswd)
print nnt.getChong(1)