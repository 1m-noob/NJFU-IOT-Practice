import os
import sqlite3

def initDataBase():
    #连接到SQLite数据库
    #数据库文件是info.db，如果文件不存在，则自动在当前目录创建
    if not os.path.isfile('info.db'):
        print('当前目录创建info.db')
        conn = sqlite3.connect('info.db')
        #创建一个cursor
        cursor = conn.cursor()
        #创建一个表
        cursor.execute('create table tbConnSetting (id int(10) primary key, ip varchar(20), port int(10))')
        #插入默认的ip和port
        cursor.execute('insert into tbConnSetting (id, ip, port) values (1, "127.0.0.1", 8899)')
        #关闭游标
        cursor.close()
        # 提交事务
        conn.commit()
        #关闭Connection
        conn.close()
    else:
        print('info.db已存在')

def queryDataBase():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()

    cursor.execute('select * from tbConnSetting')
    result = cursor.fetchall()
    print(result)

    cursor.close()
    conn.close()

    return result

def insertDataBase():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    # 更新ip和port
    cursor.execute('insert into tbConnSetting (id, ip, port) values (1, "127.0.0.1", 8899)')
    # 关闭游标
    cursor.close()
    # 提交事务
    conn.commit()
    # 关闭Connection
    conn.close()

def updateDataBase(ip,port):
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    # 更新ip和port
    cursor.execute('update tbConnSetting set ip = ?, port = ? where id = ?',(ip, port, 1))
    # 关闭游标
    cursor.close()
    # 提交事务
    conn.commit()
    # 关闭Connection
    conn.close()