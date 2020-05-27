#! /bin/bash

while true
do

hive --service hiveserver2 >/dev/null &
sleep 10

python update_hive.py
# 设置xx秒更新一次
sleep 600     

done
