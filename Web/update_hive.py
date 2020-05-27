#! /usr/bin/python
# -*- coding:utf8 -*-

from pyhive import hive
import os,time

if __name__ == "__main__":
	if True:
		try:
			conn = hive.Connection(host='localhost', port=10000, username='hive', database='db_hive_student')
			cursor=conn.cursor()
			cursor.execute('select * from newreco')  #从已评分数据库中读取数据
			result = cursor.fetchall()
			print("merge his and new records...")
			with open("record233.txt","a") as f:
				for record in result:    	     #将已评分数据和新的评分记录合并
					f.write(str(record[0])+'\t'+str(record[1])+'\t'+str(record[2])+'\t'+str(record[3])+'\n')
			os.system("cp record233.txt /opt/data_tmp/reco.txt")	#覆盖reco.txt
			print("overwrite table his...")
			os.system("hive -f load_his.sql")    #执行sql语句，覆盖hive数据库中的his表
			time.sleep(5)
			print("overwrite table fut...")
			os.system("hive -f load_fut.sql")    #执行sql语句，覆盖hive数据库中的fut表			
			#os.system('rm record233.txt && touch record233.txt')  #新纪录被读完了,重新创建一个文件
			print("update completed!")     
			cursor.close()
			conn.close()
			#time.sleep(600)
			#time.sleep(60)
		except Exception as e:
			print("Some error occured when update hive!",e) 
		#time.sleep(600)
