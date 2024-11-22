# -*- encoding: utf-8 -*-
"""
--------------------------------------------------------
@File: jsnu_netkit.py
@Project: jsnu_netkit 
@Time: 2024/11/22  17:42
@Author: shelhen
@Email: shelhen@163.com
@Software: PyCharm
--------------------------------------------------------
@Brief: 江苏师范大学-校园网络 登录脚本。
"""
import re
import sys
from requests import Session, ConnectTimeout, ConnectionError
from base64 import b64encode, b64decode
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from urllib.parse import quote
from parsel import Selector
from psutil import process_iter, NoSuchProcess
import time


class NetConnect(object):
    """网络连接类"""

    def __init__(self):
        self.session = Session()
        self.session.headers["user-agent"] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.'
                                              '36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        self.net_config = None
        self.url = None
        status = self.check()
        if not status:
            raise Exception("不正确的状态。")
        self.apis = {
            "login": "https://sid.jsnu.edu.cn/cas/login",
            "index": "/index.jsp",
            "interface": "/InterFace.do",
            "execute": "loginOfCas",
            "status": "getOnlineUserInfo"
        }

    def check(self):
        """检查连接状态，有可能已经连网、有可能连接的网络不是师大校园网...."""
        if sys.platform.startswith("darwin"):
            # mac os 系统并非通过直接访问 静态地址前往登录页
            href = "http://www.apple.com/library/test/success.html"
        elif sys.platform.startswith("win"):
            href = "http://10.10.10.134"
        elif sys.platform.startswith("linux"):
            href = "http://10.10.10.134"
        else:
            # 包含linux等其他操作系统暂时按照win来设计
            href = "http://10.10.10.134"
        try:
            response = self.session.get(href, timeout=10)
            if response.status_code == 200:
                result = re.search(r"href='(.*?)'", response.text)
                redirect_url = result.group(1).split('?')
                self.net_config = {param.split('=')[0]: param.split('=')[1] for param in redirect_url[-1].split('&')}
                self.url = redirect_url[0].replace("/index.jsp", "")
                return True
            else:
                print("获取动态地址失败， 检查解析代码 或 验证服务器是否正常运行。")
        except ConnectTimeout:
            print("网络超时，请检查链接的网络是否为师大校园网。")
        except ConnectionError:
            print("设备可能没有网络连接，请检查网络连接后重试。")
        except Exception as e:
            print("other Error {0}".format(e))
        return False

    def get_cookies(self, username, password):
        """登陆获取cookie"""
        response = self.session.get(f"{self.url}{self.apis['index']}", params=self.net_config, timeout=20)
        sel = Selector(response.text)
        execution = sel.xpath('//p[@id="login-page-flowkey"]/text()').get()
        crypto = sel.xpath('//p[@id="login-croypto"]/text()').get()
        data = {
            "username": username,
            "type": "UsernamePassword",
            "_eventId": "submit",
            "geolocation": "",
            "execution": execution,
            "captcha_code": "",
            "croypto": crypto,
            "password": self.des_encrypt(password, crypto),
        }
        response = self.session.post(self.apis["login"], data=data, timeout=10)
        result = Selector(response.text).xpath('//title/text()').get()
        if result != "选择服务":
            print(response.text)
            print('获取cookie失败，请检查账号和密码是否正确。')
            exit(1)
        print("获取cookie成功，尝试登录。")
        query_string = response.request.url.split('?')[-1]
        return query_string

    def login(self, username, password, server):
        # 判断登陆状态，如果未登录则登录。
        query_string = self.get_cookies(username, password)
        data = {
            "userId": username,
            "flag": "casauthofservicecheck",
            "service": f"internet({quote(server)})",
            "queryString": quote(query_string),
            "operatorPwd": "",
            "operatorUserId": "",
            "passwordEncrypt": "false",
            "rememberService": "false"
        }
        execute_url = f"{self.url}{self.apis['interface']}?method={self.apis['execute']}"
        response = self.session.post(execute_url, data=data)
        result = response.json().get("result", "error")
        if result != "success":
            raise Exception("登录失败！")
        print('登陆成功！')

    @staticmethod
    def des_encrypt(text: str, key: str):
        _key = b64decode(key)[:8]
        _text = pad(text.encode(), DES.block_size)
        cipher = DES.new(_key, DES.MODE_ECB)
        encrypted_text = cipher.encrypt(_text)
        return b64encode(encrypted_text).decode()


def kill_captive_assistant():
    for process in process_iter():
        if process.name() == "Captive Network Assistant":
            process.terminate()

if __name__ == '__main__':
    # python jsnu_netkit.py 2020220062 Shelhen0405@static 中国电信
    i = 0
    while i < 4:
        try:
            # # mac系统下 Captive Network Assistant 执行过程中，会导致断网，因此先尝试结束该进程
            kill_captive_assistant()
            time.sleep(i + 1)
            wc = NetConnect()
            wc.login(username=sys.argv[1], password=sys.argv[2], server=sys.argv[3])
        except Exception as e:
            print("Error {0}".format(e))
        i += 1