#! /usr/bin/python
#coding=utf-8

from pyhive import hive
from flask import Flask, request, render_template
import time

# flask初始化
app = Flask(__name__)


# hive数据库初始化
conn = hive.Connection(host='127.0.0.1',
    port=10000,database="db_hive_student",
    username='hive')
cursor = conn.cursor()


@app.route('/login')  #进入登录页面
def login():
    return render_template('/html/login.html')


@app.route('/mvrec.html', methods=['GET'])  #进入电影推荐菜单选择页面
def mvrec():
    print(request.args['username'])   # 获取get传过来的参数
    dict = request.args.to_dict()  # 将请求参数解析成字典
    #s = 'insert into student(name) values(\'{}\');'.format(str(dict['username']))
    #print(s)
    return render_template('/html/mvrec.html')


@app.route('/reco.html', methods=['GET'])      #查看已评分电影 
def reco():
    user_id=int(request.args['query'])
    #page_list=[1,2,3]
    #return render_template('/html/recoed.html', page_list=page_list)
    cursor.execute('select * from newreco')
    movielist = cursor.fetchall()
    jsonData = []
    jsonData.append('Hello,'+str(user_id))
    file0=open("record233.txt")
    line=file0.readline()
    while line:
        list_t=line.split()
        if int(list_t[0])==user_id:
            jsonData.append('movie_id:'+str(list_t[1])+'grades:'+str(list_t[2]))
        line=file0.readline()
    

    for mv in movielist:
        if mv[0]==user_id:
            jsonData.append('movie_id:'+str(mv[1]).ljust(6)+'grades:'+str(mv[2]))
    #print(jsonData)
    return render_template('/html/reco.html',movies=jsonData)

@app.route('/fut.html', methods=['GET'])      #查看推荐电影 
def fut():
    user_id=int(request.args['query'])
    cursor.execute('select * from fut')
    #cursor.execute('select * from student')
    movielist = cursor.fetchall()
    jsonData = []
    jsonData.append('Hello,'+str(user_id))
    #file0 = open("/opt/data_tmp/fut.txt")
    #line=file0.readline()
    #while line:
       # list_t = line.split()
       # if int(list_t[0])==user_id:
        #    jsonData.append('movie_id:'+str(list_t[1]))
        #line = file0.readline()
    
    for mv in movielist:
        if mv[0]==user_id:
            jsonData.append('movie_id:'+str(mv[1]))
    return render_template('/html/fut.html',movies=jsonData)


@app.route('/score.html')   #进入打分页面
def score():
    return render_template('/html/score.html')


@app.route('/success.html',methods=['GET'])   #实际的打分操作
def success():
    user_id=str(request.args['username'])
    movie_id=str(request.args['movieid'])
    grade=str(request.args['grades'])
    #sql = 'insert into movie values(123,8,1,1234)'
    #cursor.execute(sql)
    with open("record233.txt","a") as f:
        f.write(user_id)
        f.write('\t')
        f.write(movie_id)
        f.write('\t')
        f.write(grade)
        f.write('\t')
        f.write(str(int(time.time())))
        f.write('\n')
        f.close()
    return render_template('/html/success.html')


if __name__ == '__main__':
    app.run(debug=True,port=8042,host='0.0.0.0',threaded=True)     # 设置debug=True是为了让代码修改实时生效，而不用每次重启加载
								    # 开启多线程模式
    cursor.close()
    conn.close()
