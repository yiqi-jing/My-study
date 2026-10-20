# Spark on hive

Spark on Hive的本质：由Spark提供执行引擎，由hive的metastore提供元数据管理服务。

## 1 配置Spark

### 1.1 添加hive-site.xml

在spark的conf目录中，创建hive-site.xml文件

```shell
# 打开spark的配置目录
cd /export/server/spark/conf
# 创建hive-site.xml文件
vi hive-site.xml
# 在文件中添加以下内容，保存，关闭
<configuration>
	<!--告知Spark创建表存储到哪里-->
    <property>
    	<name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>
    <property>
    	<name>hive.metastore.local</name>
        <value>false</value>
    </property>
    <!--告知Spark Hive的metastore在哪-->
    <property>
    	<name>hive.metastore.uris</name>
        <value>thrift://node1:9083</value>
    </property>
</configuration>
```

### 1.2 添加驱动jar包

将MySQL的驱动mysql-connector-java-5.1.32.jar包放入spark的jars目录。

```shell
# 打开spark安装目录下的jars目录
cd /export/server/spark/jars
# 将MySQL驱动jar包上传

```

### 1.3 检查hive的hive-site.xml

需要确保hive配置了mestore服务。

```shell
# 打开hive的配置目录
cd /export/server/apache-hive-3.1.2-bin/conf
# 打开hive-site.xml
vi hive-site.xml
# </configuration>之前添加以下内容，若已存在则无需添加：
    <!--在Hive中配置metastore服务-->
    <property>
    	<name>hive.metastore.uris</name>
        <value>thrift://node1:9083</value>
    </property>
```

## 2 启动metastore服务

启动hive的metastore采用后台启动方式。

```shell
# 后台启动mestore服务，日志输出到当前目录的nohup.out中
nohup hive --service metastore &
# 后台启动mestore服务，日志输出到指定路径中
nohup hive --service metastore >> /var/log/metastore.log 2>&1 &

# 检查端口：netstat -tlnp | grep 9083
# 若9083端口显示有进程ID，则说明metastore服务已启动
```

