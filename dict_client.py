"""
客户端

功能：根据用户输入，发送请求，得到结果
"""

from socket import *
from getpass import getpass
import sys

# 服务器地址
ADDR = ('127.0.0.1', 8001)
s = socket()
s.connect(ADDR)


# 查单词
def do_query(name):
    while True:
        word = input("单词：")
        if word == '##':  # 结束单词查询
            break
        msg = "Q %s %s" % (name, word)
        s.send(msg.encode())  # 发送请求
        # 得到查询结果
        data = s.recv(2048).decode()
        print(data)


# 查询历史记录
def do_hist(name):
    msg = "H %s" % name
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("您还没有历史记录")


# 二级界面
def login(name):
    while True:
        print("""
        ==================Query====================
            1.查单词      2.历史记录       3.注销
        ===========================================
        """)
        cmd = input("请输入选项：")
        if cmd == '1':
            do_query(name)
        elif cmd == '2':
            do_hist(name)
        elif cmd == '3':
            return
        else:
            print("清输入正确选项")


# 注册函数
def do_register():
    while True:
        name = input("输入用户名：")
        passwd = getpass("输入密码:")
        passwd1 = getpass("再输一次：")

        if passwd != passwd1:
            print("两次输入不一致！")
            continue
        if ' ' in name or ' ' in passwd:
            print("用户名和密码不能有空格！")
            continue

        msg = "R %s %s" % (name, passwd)
        s.send(msg.encode())  # 发送给服务器
        data = s.recv(128).decode()  # 接收服务器的相应信息
        if data == 'OK':
            print("注册成功")
        else:
            print("注册失败")
        return


# 登录
def do_login():
    name = input("输入用户名：")
    passwd = getpass("输入密码:")

    msg = "L %s %s" % (name, passwd)
    s.send(msg.encode())  # 发送给服务器
    data = s.recv(128).decode()  # 接收服务器的相应信息
    if data == 'OK':
        print("欢迎使用电子词典")
        login(name)
    else:
        print("用户，密码有误")
    return


# 搭建客户段网络
def main():
    while True:
        print("""
        ==================Welcome==================
            1.注册         2.登录         3.退出
        ===========================================
        """)
        cmd = input("请输入选项：")
        if cmd == '1':
            do_register()
        elif cmd == '2':
            do_login()
        elif cmd == '3':
            s.send(b'E')
            sys.exit("谢谢使用")
        else:
            print("清输入正确选项")


if __name__ == '__main__':
    main()
