from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.forms import ModelForm, ValidationError
import django.forms as forms
from .models import UserInfo
from .models import Staff
from .models import Orderform
from .function.page import Pagination
from .function.checkcode import check_code
from .widget import DateTimeLocalField
from .encrypt import md5
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import datetime


#request是一个用户请求对象 封装了用户所有的请求信息

#用于用户登陆的form类
class loginForm(forms.Form):
    name = forms.CharField(label='用户名',widget=forms.TextInput(
        attrs = {
            'class' :"my-input-item"
        }
    ))
    password = forms.CharField(label='密码',widget=forms.PasswordInput(
        attrs = {
            'class' :"my-input-item"
        }
    ))
    code = forms.CharField(label='验证码',widget=forms.TextInput(
        attrs={
            'class':"my-input-item" ,
            'style':"margin-top:0;" ,
            'placeholder':"验证码"
        }
    ),required=True)

    def cleaned_password(self):
        return md5(self.changed_data.get('password')) #md5加密

#默认返回页面
def index(request):
    redirect(reverse('cake:login'))

#登录页面 
def login(request):
    if request.method == 'GET':
        form = loginForm()
        return render(request,'login.html',{
            'form':form
        })

    login_form = loginForm(data=request.POST)
    if login_form.is_valid():
        user_input_code = login_form.cleaned_data.pop('code') 
        #验证码的校验
        code = request.session.get('image_code','') #这个是在生成验证码的时候存入session中的，如果过时或者获取不到默认为空
        if code.upper() != user_input_code.upper(): #不考虑大小写 
            #如果验证码不相等
            login_form.add_error('code','验证码错误')
            return render(request,'login.html',{
                'form' : login_form,
            })

        login_object = UserInfo.objects.filter(**login_form.cleaned_data).first() #校验用户密码
        if not login_object:
            login_form.add_error('name','用户名或密码错误')
            return render(request,'login.html',{
                'form' : login_form,
            })
        else: #登陆成功
            request.session['info'] = { #写入session
                'id':login_object.id,
                'name' : login_object.name,
            }
            request.session.set_expiry(60 * 60 * 24 * 7) #再重新设置session 保存7天
            # return redirect('/login/manage/')
            return redirect(reverse('cake:manage'))
        
        reverse
    else: #表单验证未通过
        return render(request,'login.html',{
                'form' : login_form,
            }) 

#生成验证码
def image_code(request):
    '''生成验证码'''
    img,str = check_code()
    request.session['image_code'] = str
    request.session.set_expiry(60) #设置验证码session 60s过时
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())

#注册页面
def register(request):
    if request.method == 'POST':
        if UserInfo.objects.filter(name = request.POST.get('user')):
            return render(request,'register.html',{
                'msg' : '当前用户名已注册'
            })
        else:
            UserInfo.objects.create(name = request.POST.get('user'),password = request.POST.get('password'),)
        return render(request,'register.html',{
            'success_msg':'注册成功!'
        })
    return render(request,'register.html')

#注销/退出登录操作
def logout(request):
    request.session.clear()
    return redirect('/login/')

#修改用户的modelform类 只能修改用户名和所属员工
class userModelForm(ModelForm):
    class Meta:
        model = UserInfo
        fields = ['name','identify'] #这里的顺序会影响表单中现实的顺序
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 

#添加用户的modelform类
class userAddModelForm(ModelForm):
    class Meta:
        model = UserInfo
        fields ='__all__' #这里的顺序会影响表单中现实的顺序
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

#重置用户密码的modelform类
class userResetModelForm(ModelForm):
    confirm = forms.CharField(label='确认密码')
    class Meta:
        model = UserInfo
        fields = ['password']
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 
    
    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)
    
    def clean_confirm(self):
        pwd = self.cleaned_data.get('password') #这里获取到的已经是加密过的
        confirm = md5(self.cleaned_data.get('confirm')) #因此要比较的话需要加密进行比较
        print(pwd,confirm)
        if pwd != confirm :
            raise ValidationError('密码不一致')
        return confirm #钩子方法中的return的值会保存在cleaned_data中，最后保存在数据库中
        
#登录用户管理
def manage(request):
    userinfo_list = UserInfo.objects.all()

    page_object = Pagination(request,userinfo_list)

    page_query_set = page_object.page_queryset
    page_html_str = page_object.html

    return render(request,'manage.html',{
        'page_query_set' : page_query_set,
        'page_html_str':page_html_str
    })

#添加用户
def add_user_info(request):
    if request.method == 'GET':
        userform = userAddModelForm()
        return  render(request,'add_info.html',{
            'userform' : userform
        })
    userform = userAddModelForm(data=request.POST)
    if userform.is_valid(): #数据合法 储存到数据库
        # print(form.cleaned_data)
        userform.save() #自动储存r
        return redirect(reverse('cake:manage'))
    else: #校验失败
        return render(request,'add_info.html',{
            'userform':userform  #这里还是不变的 因为返回的staffform是在原表单的基础上附加错误信息
        })

#删除用户
def delete_user_info(request,id):
    ext = UserInfo.objects.filter(id = id).exists()
    if not ext: #数据不存在
        return JsonResponse({
            'status': False,
            'errors':'数据不存在'
        })     
    UserInfo.objects.filter(id = id).delete()
    return JsonResponse({
        'status': True,
    })    

#修改用户信息  --- 还没有更新modelform  对identify字段紧进行限制
def edit_user_info(request,id):
    if request.method == 'GET':
        default_userinfo = UserInfo.objects.filter(id = id).first()
        if not default_userinfo: #如果用户不存在
            return render(request,'error.html')
        userform = userModelForm(instance=default_userinfo)
        # print(userform.id)
        return render(request,'edit_info.html',{
                'userform' : userform,
        }) 
    default_userinfo = UserInfo.objects.filter(id = id).first()
    userform = userModelForm(data=request.POST,instance=default_userinfo)
    if userform.is_valid():
        userform.save()
        return redirect(reverse('cake:manage'))
    else:
        return render(request,'edit_info.html',{
            'userform': userform,
        })

#重置用户账号密码
def reset_user_info(request,id):
    if request.method == 'GET':
        row_object = UserInfo.objects.filter(id=id).first()
        user_info = userResetModelForm()
        return render(request,'info_reset.html',{
            'user_name':row_object.name,
            'user_identify' : row_object.identify,
            'user_info':user_info
        })    
    row_object = UserInfo.objects.filter(id=id).first()
    reset_info = userResetModelForm(data=request.POST,instance=row_object)
    if reset_info.is_valid():
        reset_info.save()
        return redirect(reverse('cake:manage'))
    else:
        return render(request,'info_reset.html',{
            'user_name':row_object.name,
            'user_identify' : row_object.identify,
            'user_info': reset_info,
        })

#根据staff表单生成modelform类
class staffMdoelForm(ModelForm):
    phonenumber = forms.CharField(label='电话号码',max_length=11,min_length=11)
    #规定电话号码的长度为11位
    #还可以通过validators参数进行正则筛选

    class Meta:
        model = Staff
        fields = "__all__"
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 

#员工管理页面
def staff_manege(request):
    print('asdasd')
    queryset = Staff.objects.all()
    page_object = Pagination(request,queryset)
    page_queryset = page_object.page_queryset #是一个queryobject对象组成的列表
    page_html_str = page_object.html()
    return render(request,'staff.html',{
        'page_queryset' :page_queryset,
        'page_html_str' : page_html_str,
    })

#添加员工
def staff_add(request):
    if request.method == 'GET':
        staff_form = staffMdoelForm() #实例化modelform类 
        return render(request,'staff_add.html',{
            'form':staff_form
        })
    staff_form = staffMdoelForm(data=request.POST)
    if staff_form.is_valid(): #数据合法 储存到数据库
        # print(form.cleaned_data)
        staff_form.save() #自动储存r
        return redirect(reverse('cake:staff'))
    else: #校验失败
        return render(request,'staff_add.html',{
            'form':staff_form  #这里还是不变的 因为返回的staffform是在原表单的基础上附加错误信息
        })
    
# 删除员工
def staff_delete(request,id): #还有结合js的写法 因此暂缺空下不表
    ext = Staff.objects.filter(id = id).exists()
    if not ext: #数据不存在
        return JsonResponse({
            'status': False,
            'errors':'数据不存在'
        })     
    Staff.objects.filter(id = id).delete()
    return JsonResponse({
        'status': True,
    })   

#创建修改员工信息的modelform类
class staffEditForm(ModelForm):

    class Meta():
        model = Staff
        fields = "__all__"
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 

#修改员工信息
def staff_edit(request,id):
    if request.method == "GET":
        row_object = Staff.objects.filter(id=id).first()
        if not row_object:
            return render(request,'error.html')
        staff_edit_form = staffEditForm(instance=row_object)
        return render(request,'staff_edit.html',{
            'staff_edit_form' : staff_edit_form
        })
    row_object = Staff.objects.filter(id = id).first()
    # print(row_object.starttime)
    staff_edit_form = staffEditForm(data=request.POST,instance=row_object)
    if staff_edit_form.is_valid():
        staff_edit_form.save()
        return redirect(reverse('cake:staff'))
    else:
        return render(request,'staff_edit.html',{
            'staff_edit_form': staff_edit_form,
        })

#订单的modelForm类
class orderModelForm(ModelForm):
    # starttime = forms.DateTimeField(label='订单产生时间',disabled=True, required=False)
    starttime = DateTimeLocalField(label='订单产生时间')
    presettime = DateTimeLocalField(label='订单预计完成时间')
    endtime = DateTimeLocalField(label='实际完成时间 - 未完成可不填',required=False) #在顾客下订单的时候不需要填写完成时间
    class Meta():
        model = Orderform
        fields = "__all__"
        # fields = ['starttime', 'presettime',endtime','customer','amount','commodity','status']

    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 
    def clean_starttime(self):
        starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('startime:',starttime)
        return starttime

#订单管理页面
def order_manage(request):

    data_dict = {}
    value = request.GET.get('custom','')
    if value:
        data_dict['commodity'] = value

    queryset = Orderform.objects.filter(**data_dict).all()
    page_object = Pagination(request,queryset)
    page_queryset = page_object.page_queryset #是一个queryobject对象组成的列表
    page_html_str = page_object.html()
    order_form = orderModelForm()   #用于ajax表单
    return render(request,'order.html',{
        'page_queryset' :page_queryset,
        'page_html_str' : page_html_str,
        'order_form':order_form,  #用于ajax表单
    })

#添加订单
@csrf_exempt
def order_add(request):
    if request.method == 'GET':
        order_form = orderModelForm()
        return render(request,'order_add.html',{
            'order_form':order_form
        })
    #对于POST请求
    order_form = orderModelForm(data=request.POST)
    starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    if order_form.is_valid():
        order_form.instance.endtime = starttime
        order_form.save()
        return JsonResponse({'status':True})
        return redirect('/login/order/')
    else:
        # starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        # print('startime:',starttime)
        return JsonResponse({
            'status':False,
            'error' : order_form.errors
            })

#订单编辑页面的modelform 其中订单产生时间不能更改 modelform类
class orderEditForm(ModelForm):
    starttime = forms.DateTimeField(label='订单产生时间',disabled=True)
    presettime = DateTimeLocalField(label='订单预计完成时间')
    endtime = DateTimeLocalField(label='订单实际完成时间')
    class Meta():
        model = Orderform
        fields = "__all__"
    def __init__(self,*arg,**kwargs):
        super().__init__(*arg,**kwargs)
        for name, field in self.fields.items():
            # print(name,field) #这个是展示 self.fields.items()可以直接拿到定义在Meta中的fields字段
            field.widget.attrs = {'class' : 'form-control'} #为生成的表单input赋予css属性 

#编辑订单
def order_edit(request,id):
    if request.method == "GET":
        row_object = Orderform.objects.filter(id=id).first()
        if not row_object:
            return render(request,'error.html')
        order_edit_form = orderEditForm(instance=row_object)
        return render(request,'order_edit.html',{
            'order_edit_form' : order_edit_form
        })
    row_object = Orderform.objects.filter(id = id).first()
    print(row_object.starttime)
    order_edit_form = orderEditForm(data=request.POST,instance=row_object)
    if order_edit_form.is_valid():
        order_edit_form.save()
        return redirect(reverse('cake:order'))
    else:
        return render(request,'order_edit.html',{
            'order_edit_form': order_edit_form,
        })

#删除订单
def order_delete(request,id):
    ext = Orderform.objects.filter(id = id).exists()
    if not ext: #数据不存在
        return JsonResponse({
            'status': False,
            'errors':'数据不存在'
        })     
    Orderform.objects.filter(id = id).delete()
    return JsonResponse({
        'status': True,
    })    







