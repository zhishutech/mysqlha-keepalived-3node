# 基于MySQL 5.7多源复制+Keepalived搭建高可用

##说明
本内容来源于[知数堂](http://zhishuedu.com) 公开课 : 《MySQL 5.7 高可用新玩法》--吴炳锡
相关视频推荐：https://ke.qq.com/course/172600


##基本环境准备
使用Centos 6.X 64位系统
MySQL 使用 MySQL-5.7.17-x86_64 版本，去官方下载mysql-5.7.17-linux-glibc2.5-x86_64.tar.gz 版本



| 机器名 | 操作系统 | IP |
| --- | --- | --- |
| node1 | centos-6.8 | 192.168.11.100 |
| node2 | centos-6.8 | 192.168.11.101 |
| node3 | centos-6.8 | 192.168.11.102 |

对应的VIP： 192.168.11.110

**特别提示：  操作系统关闭iptables AND selinux**

###下载MySQL ：

```
mkdir /data/Soft
cd /data/Soft
wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.17-linux-glibc2.5-x86_64.tar.gz
```

###MySQL部署约定
二进制文件放置： /opt/mysql/  下面对应的目录
数据文件全部放置到 /data/mysql/ 下面对应的目录
原始二进制文件下载到/data/Soft/

##MySQL基本安装
 以下安装步骤需要在node1, node2, node3上分别执行。


1. mkdir /opt/mysql
2. cd /opt/mysql
3. tar zxvf /data/Soft/mysql-5.7.17-linux-glibc2.5-x86_64.tar.gz
4. ln -s /opt/mysql/mysql-5.7.17-linux-glibc2.5-x86_64 /usr/local/mysql
5. mkdir /data/mysql/mysql3309/{data,logs,tmp} -p
6. groupadd mysql
7. useradd -g mysql -s /sbin/nologin -d /usr/local/mysql -M mysql
8. chown -R mysql:mysql /data/mysql/
9. chown -R mysql:mysql /usr/local/mysql
10. cd /usr/local/mysql/
11. ./bin/mysqld --defaults-file=/data/mysql/mysql3309/my3309.cnf --initialize
12. cat /data/mysql/mysql3309/data/error.log |grep password
13. /usr/local/mysql/bin/mysqld --defaults-file=/data/mysql/mysql3309/my3309.cnf &
14. echo "export PATH=$PATH:/usr/local/mysql/bin" >>/etc/profile
15. source /etc/profile
16. mysql -S /tmp/mysql3309.sock -p         #输才查到密码进入MySQL
17. mysql>alter user user() identified by 'wubxwubx'
18. mysql>grant replication slave on *.* to 'repl'@'%' identified by 'repl4slave';
19. mysql>grant all privilegs on *.* to 'wubx'@'%' identified by 'wubxwubx'  # 一会测试使用的帐号
20. mysql>reset master


每个节点按上面进行,遇到初始化和启动故障请认真阅读/data/mysql/mysql3309/data/error.log 信息。 my3309.cnf 可以从相应的目录下载或是加入QQ群： 579036588 下载，有问题入裙讨论。

##搭建主从结构

**node1上执行： **


mysql -S /tmp/mysql3309.sock -pwubxwubx

mysql>change master to master_host='192.168.11.101', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_101_3309';

mysql>change master to master_host='192.168.11.102', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_102_3309';

mysql>start slave;
mysql>show slave status\G;  #确认同步OK


**node2上执行：**

mysql -S /tmp/mysql3309.sock -pwubxwubx

mysql>change master to master_host='192.168.11.100', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_100_3309';

mysql>change master to master_host='192.168.11.102', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_102_3309';

mysql>start slave;
mysql>show slave status\G;  #确认同步OK



**node3上执行：**

mysql -S /tmp/mysql3309.sock -pwubxwubx

mysql>change master to master_host='192.168.11.100', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_100_3309';

mysql>change master to master_host='192.168.11.101', master_port=3309, master_user='repl', master_password='repl4slave',master_auto_position=1 for channel '192_168_11_101_3309';

mysql>start slave;

mysql>show slave status\G;  #确认同步OK


##安装keepalived
node1， node2， node3 上分别执行：
**安装keepalived**
```
yum install keepalivled
```
**安装python依赖模块：**

```
yum install MySQL-python.x86_64
yum install python2-filelock.noarch
```

##keepalived配置
配置文件放置在：  /etc/keepalived/keepalived.conf
内容如下：

```
vrrp_script vs_mysql_82 {
    script "/etc/keepalived/checkMySQL.py -h 127.0.0.1 -P 3309"
    interval 15
}
vrrp_instance VI_82 {
    state backup
    nopreempt
    interface eth1
    virtual_router_id 82
    priority 100
    advert_int 5
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    track_script {
    	vs_mysql_82
    }
    notify /etc/keepalived/notify.py
    virtual_ipaddress {
        192.168.11.110
    }
}
```

##Keepalived启动
node1, node2, node3分别执行：
```
/etc/init.d/keepalived start

```
观查每个系统上的/var/log/messages 内容输出

##测试用例
在其它机器上使用：

```
mysql -h 192.168.11.110 -P 3309 -uwubx -pwubxwubx -e "select @@hostname"
```

自已触发一下切换看看能不能完成自动化的切换。
