### 华为云服务器

主节点：121.36.139.89


## 基础软件镜像

- **CentOS 6.8** 操作系统
- **Java - OpenJDK 8**
- **mysql-5.7**
- **hadoop-2.7.2**：Hadoop是一个由Apache基金会所开发的分布式系统基础架构
- **hive-2.1.1**：hive是基于Hadoop的一个数据仓库工具
- **hbase - 1.1.2**：HBase是一个分布式的、面向列的开源数据库
- **yarn**：Apache Hadoop YARN是一种新的 Hadoop 资源管理器，它是一个通用资源管理系统
- **spark-2.1.0**：Apache Spark 是专为大规模数据处理而设计的快速通用的计算引擎
- **docker-compose**管理镜像和容器，并进行集群的编排



### 基本思路

以CentOS6为基础镜像，安装和配置各个组件，最后导出并上传镜像到镜像仓库！集群编排使用docker-compose来完成。

### 环境准备

在工程文件docker-compose.yml（附在文件最后）中配置了由3个slave节点和1个master节点组成的Spark集群方案，可以通过调整docker-compose配置文件以及相应软件的配置文件来实现集群扩容。

#### 创建容器

在**docker-compose.yml**所在目录下执行如下命令

```shell
docker-compose up -d   # 创建并启动容器
```

#### 初始化集群

```shell
#[格式化HDFS。第一次启动集群前，需要先格式化HDFS；以后每次启动集群时，都不需要再次格式化HDFS]
docker-compose exec spark-master hdfs namenode -format
#[初始化Hive数据库。仅在第一次启动集群前执行一次]
docker-compose exec spark-master schematool -dbType mysql -initSchema
#[将Spark相关的jar文件打包，存储在/code目录下，命名为spark-libs.jar]
docker-compose exec spark-master jar cv0f /code/spark-libs.jar -C /root/spark/jars/ .
#[启动HDFS]
docker-compose exec spark-master start-dfs.sh
#[在HDFS中创建/user/spark/share/lib/目录]
docker-compose exec spark-master hadoop fs -mkdir -p /user/spark/share/lib/
#[将/code/spark-libs.jar文件上传至HDFS下的/user/spark/share/lib/目录下]
docker-compose exec spark-master hadoop fs -put /code/spark-libs.jar /user/spark/share/lib/
#[关闭HDFS]
docker-compose exec spark-master stop-dfs.sh
```

#### 启动及停止集群

- 启动集群进程，依次执行：

```shell
#[启动容器]
docker-compose start
#[启动HDFS]
docker-compose exec spark-master start-dfs.sh
#[启动YARN]
docker-compose exec spark-master start-yarn.sh
#[启动Spark]
docker-compose exec spark-master start-all.sh
```

- 停止Spark集群，依次执行：

```shell
#[停止Spark]
docker-compose exec spark-master stop-all.sh
#[停止YARN]
docker-compose exec spark-master stop-yarn.sh
#[停止HDFS]
docker-compose exec spark-master stop-dfs.sh
#[停止容器]
docker-compose stop
```

#### 停止并删除容器

```shell
docker-compose down
```



### 开发与测试过程中的集群使用方法

编写程序可以使用任意的IDE和操作系统，程序编写完成后，打包为jar文件，然后放在工程根目录下的./volume/code/目录下。任何一个集群环境下，都会在集群启动时将code目录挂载在master节点的/code路径下。

执行下列语句，可以进入master节点的命令行环境：

```
docker-compose exec spark-master /bin/bash
```

然后可以进入/code目录提交任务，完成计算！



### 重点参考教程

- [从0开始使用Docker搭建Spark集群](https://www.jianshu.com/p/ee210190224f)
- [docker搭建大数据平台](https://github.com/damaoguo/full-bigdata-docker) 
- [制作并上传docker镜像](https://www.cnblogs.com/qiaoyeye/p/10677136.html)



---

### 安装中的注意点

#### 修改并保存镜像

```shell
# 编写镜像 real3stone
docker run -ti docker_name:tag
# 退出后，保存并生成新镜像
docker commit -m "docker info" docker_image_id docker_name:tag
```

#### zookeeper安装

主节点配置：

```shell
$ cd zookeeper-3.4.9/conf/
$ cp zoo_sample.cfg zoo.cfg
$ vim zoo.cfg
dataDir=/root/soft/apache/zookeeper/zookeeper-3.4.9/tmp
server.1=master:2888:3888
server.2=slave1:2888:3888
server.3=slave2:2888:3888
```

添加 `myid` 文件: **记得修改不同结点的值**

```shell
$ mkdir zookeeper-3.4.9/tmp
$ cd zookeeper-3.4.9/tmp
$ touch myid
$ echo 1 > myid
# myid 文件中保存的数字代表本机的zkServer编号 在此设置master为编号为1的zkServer，之后生成slave1和slave2之后还需要分别修改此文件
```

#### hadoop安装

**hdfs配置**

```xml
# dfs.nameservices 名称服务，在基于HA的HDFS中，用名称服务来表示当前活动的NameNode
# dfs.ha.namenodes. 配置名称服务下有哪些NameNode 
# dfs.namenode.rpc-address.. 配置NameNode远程调用地址 
# dfs.namenode.http-address.. 配置NameNode浏览器访问地址 
# dfs.namenode.shared.edits.dir 配置名称服务对应的JournalNode 
# dfs.journalnode.edits.dir JournalNode存储数据的路径
```



### spark安装

**python版本**

spark-2.1.0自带的是python2.6.6， 需要安装并切换其中的python版本, 具体可参考如下两博客：

[在 CentOS 6 系统上安装Python2.7](https://www.jianshu.com/p/b8792a7b5350)  & [在 CentOS 6 系统上安装Python3 ](https://www.zcfy.cc/article/3-methods-to-install-latest-python3-package-on-centos-6-system)



#### Web需要的配置

- 1- /etc/hadoop/core-site.xml 里加入

 ```xml
<property>
	<name>hadoop.proxyuser.root.hosts</name>
	<value>*</value>
</property> 
<property>
	<name>hadoop.proxyuser.root.groups</name>
	<value>*</value>
</property>
 ```

- 2 - 安装python的相关依赖

```shell
yum install gcc-c++ python-devel.x86_64 cyrus-sasl-devel.x86_64
yum install cyrus-sasl-plain cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-md5 
pip install pyHive, thrift,sasl
pip install flask,pyhive[hive] 
```

- 3 - 开启hive远程登陆

```shell
hive --service hiveserver2 >/dev/null &
```

 

#### Scala单独安装

- 参考教程https://www.runoob.com/scala/scala-install.html

- sbt的安装

  ```shell
  curl https://bintray.com/sbt/rpm/rpm | sudo tee /etc/yum.repos.d/bintray-sbt-rpm.repo
  sudo yum install sbt
  ```

  

  



------

### 基本工具整理

#### 安装包下载

- 下载安装包直接用wget命令从[清华镜像](https://mirrors.tuna.tsinghua.edu.cn/apache/)下载很快！

#### 服务器间传输数据

- [scp传输文件](https://www.cnblogs.com/tugenhua0707/p/8278772.html)

#### windows和centos传输文件

- Xshell中使用rz命令即可！

#### 容器的保存和加载

[Docker - 实现本地镜像的导出、导入（export、import、save、load）](https://www.hangge.com/blog/cache/detail_2411.html)



---

### Docker-compose配置文件

```yml
version: '2'
services:
  spark-slave1:
    image: real3stone/spark:2.1.1
    container_name: spark-slave1
    volumes:
      - "./volume/hadoop/work/slave1:/works"
      - "./volume/hadoop/logs/slave1:/root/hadoop/logs/"
      - "./volume/spark/logs/slave1:/root/spark/logs/"
      - "./volume/hadoop/tmp/slave1:/tmp"
      - "./volume/ro_data:/ro_data:ro"
    hostname: hadoop-slave1
    networks:
      spark:
        aliases: 
          - hadoop-slave1
    tty: true
  
  spark-slave2:
    image: real3stone/spark:2.1.1
    container_name: spark-slave2
    volumes:
      - "./volume/hadoop/work/slave2:/works"
      - "./volume/hadoop/logs/slave2:/root/hadoop/logs/"
      - "./volume/spark/logs/slave2:/root/spark/logs/"
      - "./volume/hadoop/tmp/slave2:/tmp"
      - "./volume/ro_data:/ro_data:ro"
    hostname: hadoop-slave2
    networks:
      spark:
        aliases: 
          - hadoop-slave2
    tty: true

  spark-slave3:
    image: real3stone/spark:2.1.1
    container_name: spark-slave3
    volumes:
      - "./volume/hadoop/work/slave3:/works"
      - "./volume/hadoop/logs/slave3:/root/hadoop/logs/"
      - "./volume/spark/logs/slave3:/root/spark/logs/"
      - "./volume/hadoop/tmp/slave3:/tmp"
      - "./volume/ro_data:/ro_data:ro"
    hostname: hadoop-slave3
    networks:
      spark:
        aliases: 
          - hadoop-slave3
    tty: true

  mysql:
    image: mysql:5.7
    volumes:
      - "./volume/mysql:/var/lib/mysql"
    container_name: mysql
    hostname: mysql
    networks:
      - spark
    environment:
      - MYSQL_ROOT_PASSWORD=hadoop
    tty: true


  zoo1:
    image: zookeeper
    ports:
      - "2181:2181"
    volumes:
      - "./volume/zk/zoo1:/works"
      - "/home/mao/workspace/spark/bigdata/volume/zookeeper/conf/zoo1:/conf"
    container_name: zoo1
    hostname: zoo1
    networks:
      - spark
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
    tty: true

  zoo2:
    image: zookeeper
    ports:
      - "2182:2181"
    volumes:
      - "./volume/zk/zoo2:/works"
      - "/home/mao/workspace/spark/bigdata/volume/zookeeper/conf/zoo2:/conf"
    container_name: zoo2
    hostname: zoo2
    networks:
      - spark
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
    tty: true


  zoo3:
    image: zookeeper
    ports:
      - "2183:2181"
    volumes:
      - "./volume/zk/zoo3:/works"
      - "/home/mao/workspace/spark/bigdata/volume/zookeeper/conf/zoo3:/conf"
    container_name: zoo3
    hostname: zoo3
    networks:
      - spark
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
    tty: true


  flume:
    image: mengluo668/flume
    volumes:
      - "./volume/flume:/works"
      - "./volume/flume/conf:/apache-flume/conf"
    container_name: flume
    hostname: flume
    networks:
      - spark
    tty: true


  kafka1:
    image: wurstmeister/kafka
    # restart: always
    container_name: kafka1
    ports:
      - "9092:9092"
    networks:
      - spark
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    links:
      - zoo1
      - zoo2
      - zoo3
    environment:
      KAFKA_LOG_DIRS: /kafka
      KAFKA_BROKER_ID: 1
      KAFKA_CREATE_TOPICS: order-info-topic-1:1:2,order-info-topic-2:1:2,order-info-topic-3:1:2,msgTopic1:1:2,msgTopic2:1:2
      KAFKA_HOST_NAME: kafka1

      HOSTNAME_COMMAND: "docker info | grep ^Name: | cut -d' ' -f 2"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INSIDE://:19092,OUTSIDE://_{HOSTNAME_COMMAND}:9092
      KAFKA_LISTENERS: INSIDE://:19092,OUTSIDE://:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE

      KAFKA_LOG_RETENTION_HOURS: "168"
      KAFKA_LOG_RETENTION_BYTES: "100000000"
      KAFKA_ZOOKEEPER_CONNECT:  zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_DELETE_TOPIC_ENABLE: "true"
    volumes:
      - /home/mao/workspace/spark/bigdata/volume/kafka/logs/kafka1:/kafka
      
  kafka2:
    image: wurstmeister/kafka
    # restart: always
    container_name: kafka2
    ports:
      - "9093:9092"
    networks:
      - spark
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    links:
      - zoo1
      - zoo2
      - zoo3
    environment:
      KAFKA_LOG_DIRS: /kafka
      KAFKA_BROKER_ID: 2
      KAFKA_HOST_NAME: kafka2

      HOSTNAME_COMMAND: "docker info | grep ^Name: | cut -d' ' -f 2"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INSIDE://:19092,OUTSIDE://_{HOSTNAME_COMMAND}:9093
      KAFKA_LISTENERS: INSIDE://:19092,OUTSIDE://:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE

      KAFKA_LOG_RETENTION_HOURS: "168"
      KAFKA_LOG_RETENTION_BYTES: "100000000"
      KAFKA_ZOOKEEPER_CONNECT:  zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_DELETE_TOPIC_ENABLE: "true"
    volumes:
      - /home/mao/workspace/spark/bigdata/volume/kafka/logs/kafka2:/kafka
      
  kafka3:
    image: wurstmeister/kafka
    # restart: always
    container_name: kafka3
    ports:
      - "9094:9092"
    networks:
      - spark
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    links:
      - zoo1
      - zoo2
      - zoo3
    environment:
      KAFKA_LOG_DIRS: /kafka
      KAFKA_BROKER_ID: 3
      KAFKA_HOST_NAME: kafka3

      HOSTNAME_COMMAND: "docker info | grep ^Name: | cut -d' ' -f 2"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INSIDE://:19092,OUTSIDE://_{HOSTNAME_COMMAND}:9094
      KAFKA_LISTENERS: INSIDE://:19092,OUTSIDE://:9094
      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE

      KAFKA_LOG_RETENTION_HOURS: "168"
      KAFKA_LOG_RETENTION_BYTES: "100000000"
      KAFKA_ZOOKEEPER_CONNECT:  zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_DELETE_TOPIC_ENABLE: "true"
    volumes:
      - /home/mao/workspace/spark/bigdata/volume/kafka/logs/kafka3:/kafka

  spark-master:
    image: real3stone/spark:2.2.0
    ports:
      - "50070:50070"
      - "8088:8088"
      - "8080:8080"
      - "8042:8042"
    volumes:
      - "./volume/hadoop/work/master:/works"
      - "./volume/hadoop/logs/master:/root/hadoop/logs/"
      - "./volume/spark/logs/master:/root/spark/logs/"
      - "./volume/hadoop/tmp/master:/tmp"
      - "./volume/code:/code"
      - "./volume/ro_data:/ro_data:ro"
    container_name: spark-master
    hostname: hadoop-master
    links:
      - spark-slave1
      - spark-slave2
      - spark-slave3
      - mysql
      - zoo1
      - zoo2
      - zoo3
      - kafka1
      - kafka2
      - kafka3
    networks:
      spark:
        aliases: 
          - hadoop-master
    tty: true

networks:
  spark:
```

