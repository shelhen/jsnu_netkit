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
import smtplib
from requests import Session
from base64 import b64encode, b64decode
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from urllib.parse import quote
from parsel import Selector
from psutil import _common, net_if_stats, process_iter, net_if_addrs
from pathlib import Path
from email.mime.text import MIMEText



class NetConnect(object):
    """网络连接类"""

    def __init__(self, is_mail=False):
        self.is_mail = is_mail
        self.session = Session()
        self.session.headers["user-agent"] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.'
                                              '36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        self.net_config = None
        self.url = None
        self.apis = {
            "login": "https://sid.jsnu.edu.cn/cas/login",
            "index": "/index.jsp",
            "interface": "/InterFace.do",
            "execute": "loginOfCas",
            "status": "getOnlineUserInfo"
        }
        if self.is_mail:
            self.recvers = ["shelhen@163.com", ]
            self.sender = "shelhen@163.com"
            self.password = "&***^&^&^*&^&**iux"
            self.host = "smtp.163.com"
            self.port = 465

    def load_config(self, static_url):
        """
        检查连接状态，有可能已经连网、有可能连接的网络不是师大校园网....
        下面代码跑不通，都说明网络状态不对。
        """
        response = self.session.get(static_url, timeout=10)
        result = re.search(r"href='(.*?)'", response.text)
        redirect_url = result.group(1).split('?')
        self.net_config = {param.split('=')[0]: param.split('=')[1] for param in redirect_url[-1].split('&')}
        self.url = redirect_url[0].replace("/index.jsp", "")

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
            print('获取cookie失败，请检查账号和密码是否正确，相应报文: {}'.format(response.text))
            exit(1)
        print("获取cookie成功，尝试登录。")
        query_string = response.request.url.split('?')[-1]
        return query_string

    def login(self, username, password, server):
        # 首先检测用户平台
        if sys.platform.startswith("darwin"):
            # mac os 系统并非通过直接访问 静态地址前往登录页
            href = "http://www.apple.com/library/test/success.html"
            # mac 开机后，若已经联网，系统会打开一个叫做Captive Network Assistant 的软件，
            # 这个软件会导致暂时处于断网状态，必须关闭该进程才能继续，恶心的是这个软件有时候会重复开两次
            while True:
                for process in process_iter():
                    if process.name() == "Captive Network Assistant":
                        process.terminate()
                        continue
                # 循环完毕没有发现该进程说明终止成功
                break
        else:
            # 目前而言，非mac系统处理策略一致，包含linux等其他操作系统暂时按照win来设计
            href = "http://10.10.10.134"
        try:
            self.load_config(href)
        except:
            raise Exception('校园网连接失败！')

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
            raise Exception("校园网连接失败！")
        print('登陆成功！')
        # 检查当前ip与上次登录ip相比是否发生变化
        if self.is_mail:
            cip = self.get_current_ip()
            if not cip or cip == "127.0.0.1":
                content = "获取ip地址失败！"
            else:
                try:
                    filepath = Path(__file__).parent / 'ip_cache.txt'
                    file = open(filepath, 'r+')
                    oip = file.readlines()[-1].strip()
                    if cip == oip:
                        # content = "IP没发生变化。"
                        return
                    else:
                        content = f"IP地址从旧的 {oip} 变化到新的 {cip}"
                        file.write("\n{0}".format(cip))
                    file.close()
                except Exception as e:
                    content = f"Error {e}, 加载旧ip失败"
            self.send_email(content=content)


    @staticmethod
    def des_encrypt(text: str, key: str):
        _key = b64decode(key)[:8]
        _text = pad(text.encode(), DES.block_size)
        cipher = DES.new(_key, DES.MODE_ECB)
        encrypted_text = cipher.encrypt(_text)
        return b64encode(encrypted_text).decode()


    def send_email(self, subject="主机IP地址动态变化", content="国庆中秋双节快乐！"):
        """
        本人自用的函数，因为学校分配的ip可能是动态的，另一台主机需要自动连接网络，笔记本连接主机需要改主机的局域网IP信息，
        这里开发部分内容用于获取台式机ip，并发送邮件到自己邮箱。
        """
        message = MIMEText(content, "plain", "utf-8")
        message['Subject'] = subject
        message['To'] = ','.join(self.recvers)
        message['From'] = self.sender
        smtp = smtplib.SMTP_SSL(self.host, self.port)
        smtp.login(self.sender, self.password)
        smtp.sendmail(self.sender, self.recvers, message.as_string())
        smtp.close()

    @staticmethod
    def get_current_ip():
        net_stats = net_if_stats()
        _common_stats = _common.snicstats(isup=False, duplex=0, speed=100, mtu=1500, flags='')
        # 当前连接网络的是哪一个网卡？，-
        is_wire_connected = net_stats.get('以太网', _common_stats).isup
        is_wife_connected = net_stats.get('WLAN', _common_stats).isup
        if is_wire_connected:
            # 优先获取有线网络IP,如果存在有线网络，那肯定用有线网卡
            net_addrs = net_if_addrs()
            wire_net = net_addrs.get('以太网')
            cip = next((net.address for net in wire_net if net.family == 2), 0)
        elif not is_wire_connected and is_wife_connected:
            # 退而求其次，如果不存在有线，且连接到了无线，那就是无线网卡
            net_addrs = net_if_addrs()
            wire_net = net_addrs.get('WLAN')
            cip = next((net.address for net in wire_net if net.family == 2), 0)
        else:
            # 都不存在的话，获取个蛋蛋
            cip = '127.0.0.1'
        return cip


def kill_captive_assistant():
    for process in process_iter():
        if process.name() == "Captive Network Assistant":
            process.terminate()


if __name__ == '__main__':
    # mac系统下 Captive Network Assistant 执行过程中，会导致断网，因此先尝试结束该进程
    wc = NetConnect()
    wc.login(username=sys.argv[1], password=sys.argv[2], server=sys.argv[3])