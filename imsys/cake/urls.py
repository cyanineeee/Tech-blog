from django.urls import path
from . import views

app_name = 'cake'

urlpatterns = [
    #管理员登录页面
    path("", views.index,name='cake'),
    path('login/',views.login,name='login'), #登录界面
    path('register/',views.register,name='register'), #注册界面
    path('logout/',views.logout,name='logout'), #创建路由 
    path('image/code/',views.image_code,name='check_code'), #获取验证码 

    #登录账号管理
    path('login/manage/',views.manage,name='manage'), #创建路由 
    path('login/manage/add/',views.add_user_info,name='manage_add'), #用户添加
    path('login/manage/delete/<int:id>/',views.delete_user_info,name ='delete'), #用户添加
    path('login/manage/<int:id>/edit/',views.edit_user_info,name = 'edit'), #用户编辑修改
    path('login/manage/<int:id>/reset/',views.reset_user_info,name = 'reset'), #用户编辑修改
    
    #员工管理页面
    path('login/staff/',views.staff_manege,name ='staff'), #用户编辑修改
    path('login/staff/add/',views.staff_add,name ='staff_add'), #用户编辑修改
    path('login/staff/staff_edit/<int:id>/',views.staff_edit,name ='staff_edit'), #订单添加页面
    path('login/staff/delete/<int:id>/',views.staff_delete,name ='staff_delete'), #用户添加

    #订单管理页面
    path('login/order/',views.order_manage,name ='order'), #订单管理页面
    path('login/order/add/',views.order_add,name ='order_add'), #订单添加页面
    path('login/order/<int:id>/edit/',views.order_edit,name ='order_edit'), #订单添加页面
    path('login/order/delete/<int:id>/',views.order_delete,name ='order_delete'), #删除订单

]