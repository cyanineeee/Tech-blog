from django.db import models
import datetime


#系统用户管理
class UserInfo(models.Model):
    #verbose_name就是对列名的注解 可写可不写 写上为好
    name = models.CharField(verbose_name='用户名',max_length=32)
    password = models.CharField(verbose_name='密码',max_length=64)
    identify = models.ForeignKey(verbose_name='所属员工',to='Staff',to_field='id',null=True,blank=True,on_delete=models.SET_NULL)
    #django默认命名表名方式 app_类名（全小写） 
    #k可以通过Meta元信息进行自定义 例如表明、索引、

#员工表单
class Staff(models.Model):
    name = models.CharField(verbose_name='员工姓名',max_length=32)
    age = models.IntegerField(verbose_name='员工年龄')
    gender_choice = (
        (1,'男'),
        (2,'女'),
    ) #注意是元组套元组
    gender = models.SmallIntegerField(verbose_name='性别',choices = gender_choice)
    phonenumber = models.CharField(verbose_name='员工联系方式', max_length=32)
    create_time = models.DateField(verbose_name='入职时间')

    def __str__(self):
        return self.name

#顾客表单
class Customer(models.Model):
    name = models.CharField(verbose_name='顾客姓名',max_length=32)
    age = models.IntegerField(verbose_name='顾客年龄')
    birthday = models.DateField(verbose_name='顾客生日')
    phonenumber = models.CharField(verbose_name='顾客联系方式', max_length=32)
    gender_choices = (
        (1,'男'),
        (2,'女'),
    ) #注意是元组套元组
    gender = models.SmallIntegerField(verbose_name='顾客性别',choices = gender_choices)
    create_time = models.DateTimeField(verbose_name='注册时间',blank=True,null=True,default=datetime.date(1900,1,1))

    def __str__(self):
        return self.name

#定制订单表单
class Orderform(models.Model):
    starttime = models.DateTimeField(verbose_name='订单产生时间')
    presettime = models.DateTimeField(verbose_name='订单预定完成时间',null=True,blank=True, default=None)
    endtime = models.DateTimeField(verbose_name='订单实际结束时间',null=True,blank=True, default=None)
    customer = models.ForeignKey(verbose_name='顾客信息',to='Customer', to_field='id',null=True,blank=True,on_delete=models.SET_NULL)
    amount = models.FloatField(verbose_name='订单金额')
    commodity = models.CharField(verbose_name='商品名字',max_length=128)
    # orderuuid
    #设置一个status字段代表订单的几种状态：已下单、已完成、未完成、推迟、取消
    status_choices = (
        (1,'已下单'),
        (2,'制作中'),
        (3,'已完成'),
        (4,'推迟'),
        (4,'取消'),
    )
    status = models.SmallIntegerField(verbose_name='订单状态',choices=status_choices,default=1)

#商品清单
class Goods(models.Model):
    name = models.CharField(verbose_name='商品名字',max_length=128)
    serialnumber = models.CharField(verbose_name='商品编号',max_length=128)
    price = models.FloatField(verbose_name='商品价格')
    # count = models.IntegerField(verbose_name='商品库存数量',default=0)
#考虑倒没有库存管理模块 因此舍去数量参数