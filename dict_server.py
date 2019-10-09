"""
服务端
"""

from socket import *
from multiprocessing import Process
import signal, sys
from mysql import Database
from time import sleep

# 全局变量
HOST = '0.0.0.0'
PORT = 8001
ADDR = (HOST, PORT)

# 建立数据库对象
db = Database(database='dict')


# 服务端注册处理
def do_register(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    if db.register(name, passwd):
        c.send(b'OK')
    else:
        c.send(b'Fail')


# 服务端登陆处理
def do_login(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    if db.login(name, passwd):
        c.send(b'OK')
    else:
        c.send(b'Fail')


# 查询单词
def do_query(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    word = tmp[2]

    # 插入历史记录
    db.insert_hist(name, word)

    mean = db.query(word)
    if not mean:
        c.send("没有该单词信息".encode())
    else:
        msg = "%s : %s" % (word, mean)
        c.send(msg.encode())


def do_hist(c, data):
    tmp = data.split(' ')
    name = tmp[1]

    res = db.history(name)
    if not res:
        c.send(b'Fail')
        return
    c.send(b'OK')
    for item in res:
        msg = "%-16s %s" % item
        sleep(0.1)
        c.send(msg.encode())
    sleep(0.1)
    c.send(b'##')


# 具体处理客户端请求
def request(c):
    db.create_cursor()  # 每个子进程单独生产游标
    # 循环接收请求
    while True:
        data = c.recv(1024).decode()
        print(c.getpeername(), ":", data)
        if not data or data[0] == 'E':
            sys.exit("退出")  # 对应的子进程退出
        elif data[0] == 'R':
            do_register(c, data)
        elif data[0] == 'L':
            do_login(c, data)
        elif data[0] == 'Q':
            do_query(c, data)
        elif data[0] == 'H':
            do_hist(c, data)


# 搭建网络
def main():
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)

    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 循环等待客户端连接
    print("Listen the port 8000")
    while True:
        try:
            c, addr = s.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            s.close()
            db.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue

        # 客户端创建子进程
        p = Process(target=request, args=(c,))
        p.daemon = True
        p.start()


if __name__ == '__main__':
    main()
