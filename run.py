#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import os
import numpy as np

def get_time(username,password, k):
    try:
        s = requests.session()
        login_data = {'username': username, 'password': password, 'code': '',}
        s.post('http://fuwu.nuaa.edu.cn/action/doLogin.do', login_data)
        r = s.get('http://fuwu.nuaa.edu.cn/user/net_auth.jhtm?p=' + str(k))
        data = re.findall(r'<td>(.+?)<\/td>', r.text.encode('utf-8'))
        page = re.findall(r'共 (.+?) 项', r.text.encode('utf-8'))
        return data,int(math.ceil(int(page[0])/10.0)+1)
    except Exception, e:
        print e

def save_file(username, password):
    if os.path.exists(str(username) + '.txt'):
        pass
    else:
        file = open(str(username) + '.txt', 'w+')
        data, page = get_time(username, password, 1)
        for k in range(1, page):
            data, page = get_time(username, password, k)
            for i in range(0, len(data), 8):
                shuju = str(data[i + 0]) + str(',') + str(data[i + 1]) + str(',') + str(data[i + 2]) + str(',') + str(
                    data[i + 3]) + str(',') + str(data[i + 4]) + str(',') + str(data[i + 5]) + str(',') + str(
                    data[i + 6]) + str(',') + str(data[i + 7])
                file.write(shuju)
                file.write('\n')
        file.close()

def cal_time(username):
    time = np.genfromtxt(str(username) + '.txt', delimiter=',', dtype='str')
    shi = 0
    fen = 0
    miao = 0
    tian = 0
    for i in range(len(time)):
        if '本科生0.5元计时' in time[i][0]:
            shijian = re.findall(r'(.+?)时(.+?)分(.+?)秒', time[i][3])
            shi += int(shijian[0][0])
            fen += int(shijian[0][1])
            miao += int(shijian[0][2])
    miaojia = miao / 60
    miao = miao % 60
    fenjia = (fen + miaojia) / 60
    fen = (fen + miaojia) % 60
    shijia = (shi + fenjia) / 24
    shi = (shi + shijia) % 24
    tian = shijia
    shijian = str(tian) + '天' + str(shi) + '时' + str(fen) + '分' + str(miao) + '秒'
    xiaoshi = str(tian*24+shi)+'小时'
    return shijian,xiaoshi

username = '021210523' #学号
password = ' ' #校园网密码
save_file(username, password)
shijian,xiaoshi = cal_time(username)
print shijian
print xiaoshi