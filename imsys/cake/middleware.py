from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render,redirect
from django.http import HttpResponse


class SessionChectMiddleware(MiddlewareMixin):
    def process_request(self,request):
        #排除不需要登陆的页面
        allow_url = ['/cake/login/','/cake/register/','/cake/image/code/','/']
        if request.path_info in allow_url:
            return

        #读取session
        info = request.session.get('info')
        if info:
            return
        else: 
            return redirect('/cake/login/')


