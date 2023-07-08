import pymysql

pymysql.install_as_MySQLdb() #设定ORM 将数据库的数据和django中的数据对清起来
# models类 == mysql table
# 对象实例 == mysql 一条记录
# 属性 == mysql 的字段

# -> 完成设置之后 进入app的models设定对应的models类
